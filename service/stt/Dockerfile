# service/stt/Dockerfile

FROM python:3.10-slim

# 1. 安装系统依赖并升级 pip
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      sox \
      build-essential \
      libffi-dev \
      libssl-dev \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --upgrade pip

WORKDIR /app

# 2. 复制并安装 STT 服务专用的 Python 依赖
# <-- 使用 STT 自己的 requirements.txt
COPY ./service/stt/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 3. 复制 STT 服务代码
COPY service/stt/stt_breeze.py .

# 创建 /models/asr25 目录，用于模型文件挂载
RUN mkdir -p /models/asr25

EXPOSE 8001

# 4. 启动 Uvicorn
CMD ["uvicorn", "stt_breeze:app", "--host", "0.0.0.0", "--port", "8001"]


