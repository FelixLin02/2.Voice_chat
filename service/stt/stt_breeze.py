# service/stt/stt_breeze.py

import os
import uuid
import shutil
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

# 导入 Hugging Face 相关的库
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torchaudio
import torch # 假设使用 PyTorch

app = FastAPI()

# MR-Breeze ASR 模型路徑或 Hugging Face 模型 ID
# 建议直接使用 Hugging Face ID，模型会在第一次加载时自动下载
MR_MODEL_ID = os.getenv("MR_BREEZE_MODEL_ID", "MediaTek-Research/Breeze-ASR-25")

processor = None
model = None

# 在应用启动时加载模型，确保只加载一次
@app.on_event("startup")
async def load_asr_model():
    global processor, model
    try:
        print(f"Loading ASR model: {MR_MODEL_ID}...")
        processor = WhisperProcessor.from_pretrained(MR_MODEL_ID)
        model = WhisperForConditionalGeneration.from_pretrained(MR_MODEL_ID)

        # 如果有 GPU，将模型移动到 GPU
        if torch.cuda.is_available():
            model = model.to("cuda")
            print("ASR model moved to GPU.")
        else:
            print("ASR model loaded on CPU.")
        model.eval() # 设置为评估模式
        print("ASR model loaded successfully.")
    except Exception as e:
        print(f"Failed to load ASR model: {e}")
        # 在生产环境中，这里可能需要更健壮的错误处理，例如退出应用
        raise RuntimeError(f"Failed to load ASR model: {e}")

@app.post("/") # 这是独立服务，路径是 /
async def transcribe(audio: UploadFile = File(...)):
    if processor is None or model is None:
        raise HTTPException(status_code=503, detail="ASR model not loaded yet. Please wait or check logs.")

    print(f"Received audio for transcription: {audio.filename}, type: {audio.content_type}")

    # 确保 /tmp 目录有写入权限，且能被清理
    tmp_dir = Path("/tmp") / str(uuid.uuid4())
    tmp_dir.mkdir(parents=True, exist_ok=True)
    webm_path = tmp_dir / "input.webm"
    wav_path = tmp_dir / "input.wav" # 即使是 WebM，也可能需要转成 WAV 或直接处理

    try:
        # 将上传的 WebM 文件写入临时文件
        with open(webm_path, "wb") as f:
            f.write(await audio.read())

        # 使用 torchaudio 加载并处理音频
        # torchaudio 可以直接加载多种格式，包括 WebM (如果安装了必要的后端如 sox/ffmpeg)
        try:
            waveform, sample_rate = torchaudio.load(str(webm_path))
            print(f"Loaded audio: sample_rate={sample_rate}, shape={waveform.shape}")
        except Exception as e:
            print(f"Torchaudio failed to load audio: {e}")
            # 尝试使用 ffmpeg 转换到 WAV，然后 torchaudio 加载 WAV
            cmd_ff = ["ffmpeg", "-y", "-i", str(webm_path), "-ar", "16000", "-ac", "1", str(wav_path)]
            res = subprocess.run(cmd_ff, capture_output=True)
            if res.returncode != 0:
                print(f"FFmpeg conversion failed: {res.stderr.decode()}")
                raise HTTPException(500, detail="Audio conversion (WebM to WAV) failed")
            
            waveform, sample_rate = torchaudio.load(str(wav_path))
            print(f"Converted to WAV and loaded: sample_rate={sample_rate}, shape={waveform.shape}")


        # 如果需要重采样或转换通道
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)
            sample_rate = 16000 # 更新采样率
        if waveform.shape[0] > 1: # 如果是多通道，转为单通道
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # 从 waveform 获取 input features
        # squeeze() 移除单维度，例如 (1, N) 变为 (N,)
        input_features = processor(waveform.squeeze().numpy(), sampling_rate=sample_rate, return_tensors="pt").input_features

        # 如果有 GPU，将输入特征移动到 GPU
        if torch.cuda.is_available():
            input_features = input_features.to("cuda")

        # 调用 Breeze ASR 模型进行推断
        predicted_ids = model.generate(input_features)
        transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        print(f"Transcription result: {transcription}")

        # STT 服务只返回转录文本，不直接操作数据库
        return JSONResponse({"text": transcription})

    except Exception as e:
        print(f"Error during ASR transcription: {e}")
        raise HTTPException(status_code=500, detail=f"ASR transcription failed: {e}")
    finally:
        # 清理临时文件
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
            print(f"Cleaned up temporary directory: {tmp_dir}")





