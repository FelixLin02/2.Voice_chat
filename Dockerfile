# Dockerfile (根目录，用于构建 app 服务)

# 使用輕量級 Python 3.10 映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製並安裝 app 服務專用相依套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY app ./app
COPY static ./static

# 创建 /data 目录，用于数据库文件挂载
RUN mkdir -p /data

# 開放 8000 埠口
EXPOSE 8000

# 啟動 FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]