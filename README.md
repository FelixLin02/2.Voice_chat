語音聊天互動介面專案
這是一個基於 FastAPI 和 Docker Compose 的語音聊天互動介面專案。它允許使用者透過語音輸入與大型語言模型 (LLM) 進行互動，並將語音轉文字 (STT) 和 LLM 回覆的過程模組化為獨立的微服務。

1. 檔案與目錄結構
本專案採用微服務架構，主要目錄和檔案的用途如下：
```
TEST_STT_LLM/
├── app/                      # 主應用程式邏輯和資料庫模組
│   ├── __init__.py           # 標示 'app' 為 Python 套件 (package)
│   ├── chat.db               # SQLite 資料庫檔案 (暫時隱藏)
│   ├── db.py                 # 資料庫操作模組 (SQLite 連結、儲存對話)
│   └── main.py               # 主應用程式，作為 API Gateway 處理前端請求，並轉發至 STT/LLM 服務
├── models/                   # 存放大型模型檔案
│   └── asr25/                # 聯發科 Breeze ASR 25 模型檔案 (由 STT 服務掛載)
├── service/                  # 各個微服務的程式碼和 Dockerfile
│   ├── llm/                  # 大型語言模型 (LLM) 服務
│   │   ├── Dockerfile        # LLM 服務的 Docker 建置配置
│   │   ├── llm_openai.py     # LLM 服務的核心程式碼 (使用 OpenAI GPT)
│   │   └── requirements.txt  # LLM 服務所需的 Python 依賴
│   └── stt/                  # 語音轉文字 (STT) 服務
│       ├── Dockerfile        # STT 服務的 Docker 建置配置
│       ├── requirements.txt  # STT 服務所需的 Python 依賴 (包含 transformers, torch, torchaudio)
│       └── stt_breeze.py     # STT 服務的核心程式碼 (使用聯發科 Breeze ASR 25 模型)
├── static/                   # 前端靜態檔案
│   └── index.html            # 網頁使用者介面 (錄音、顯示對話)
├── .env                      # 環境變數配置檔案 (存放 API Keys 等敏感資訊)
├── docker-compose.yml        # Docker Compose 配置檔案，定義並協調所有服務的啟動
├── Dockerfile                # 主應用程式 (app 服務) 的 Docker 建置配置
└── requirements.txt          # 主應用程式 (app 服務) 所需的 Python 依賴
```
建置並啟動 Docker 服務

```
docker compose up --build

```


瀏覽器
```
http://localhost:8000
```
