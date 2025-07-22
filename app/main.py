# app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx # 需要安装 httpx 库
from app.db import save_text, save_reply, init_db # 导入 db 模块的函数

app = FastAPI()

# 在应用启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Main app started and database initialized.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 开发环境方便，生产环境请指定前端域名，例如: ["http://localhost:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 前端请求 STT 的新端点
@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    接收前端音频，转发给独立的 STT 服务进行转录。
    """
    print(f"Received audio file: {audio.filename}, content_type: {audio.content_type}")
    try:
        async with httpx.AsyncClient() as client:
            # 调用独立的 STT 服务 (使用 Docker Compose 服务名 'stt' 和端口 '8001')
            # STT 服务本身的根路径就是 /
            stt_response = await client.post(
                "http://stt:8001/", # <-- 调用 stt 服务
                files={"audio": (audio.filename, await audio.read(), audio.content_type)}
            )
            stt_response.raise_for_status() # 检查 STT 服务是否返回成功状态码
            stt_result = stt_response.json()
            user_text = stt_result.get("text", "")
            print(f"STT result: {user_text}")
            # 在这里保存用户语音识别的文本到数据库
            save_text("user", user_text)
            return JSONResponse({"text": user_text})
    except httpx.HTTPStatusError as e:
        print(f"STT service responded with error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"STT service error: {e.response.text}")
    except Exception as e:
        print(f"Error forwarding to STT service: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error when calling STT: {e}")

# 前端请求 LLM 的新端点
@app.post("/api/generate_llm_response")
async def generate_llm_response(request_body: dict):
    """
    接收前端文字，转发给独立的 LLM 服务获取回覆。
    """
    user_text = request_body.get("text", "")
    print(f"Received text for LLM: {user_text}")
    if not user_text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request body for LLM.")

    try:
        async with httpx.AsyncClient() as client:
            # 调用独立的 LLM 服务 (使用 Docker Compose 服务名 'llm' 和端口 '8002')
            # LLM 服务本身的根路径就是 /
            llm_response = await client.post(
                "http://llm:8002/", # <-- 调用 llm 服务
                json={"text": user_text} # 确保数据格式与 llm_openai.py 预期一致
            )
            llm_response.raise_for_status()
            llm_result = llm_response.json()
            reply_text = llm_result.get("reply", "")
            print(f"LLM reply: {reply_text}")
            # 统一在此处保存完整的对话到数据库
            save_reply(user_text=user_text, reply=reply_text) # 保存用户提问和AI回复
            return JSONResponse({"reply": reply_text})
    except httpx.HTTPStatusError as e:
        print(f"LLM service responded with error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"LLM service error: {e.response.text}")
    except Exception as e:
        print(f"Error forwarding to LLM service: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error when calling LLM: {e}")

# 挂载静态文件服务，用于提供 index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")
