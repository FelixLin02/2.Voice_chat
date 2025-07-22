# service/llm/Dockerfile

FROM python:3.10-slim

# 1. 安装系统更新与编译工具、升级 pip
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
     build-essential \
     libffi-dev \
     libssl-dev \
     && rm -rf /var/lib/apt/lists/* \
     && pip install --upgrade pip

WORKDIR /app

# 2. 复制 requirements.txt 并安装所有 Python 依赖
COPY service/llm/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 复制 LLM 服务代码
COPY service/llm/llm_openai.py ./llm_openai.py
# 如果有共用模块 (e.g. app/db.py)，也一并复制
COPY app ./app

EXPOSE 8002

# 4. 启动 Uvicorn 服务
CMD ["uvicorn", "llm_openai:app", "--host", "0.0.0.0", "--port", "8002"]

