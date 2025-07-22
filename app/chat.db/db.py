# app/db.py
import sqlite3
from datetime import datetime
import os

# DB_PATH 應指向 db 服務掛載的共享目錄
# 在 app 容器中，這個路徑應指向 db 服務的 volume 掛載點
# 注意：在 docker-compose.yml 中，db 服務的 volume 是 ./app/chat.db:/data/chat.db
# 所以在 app 服務中，我们应该访问 /data/chat.db
DB_PATH = "/data/chat.db"

def init_db():
    """初始化資料庫表結構，如果表不存在則創建。"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()
        print(f"Database initialized or already exists at {DB_PATH}")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

def save_text(role: str, content: str):
    """
    儲存一筆訊息到 conversation 表，
    role 可以是 'user' 或 'assistant'
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        timestamp = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO conversation (role, content, timestamp) VALUES (?, ?, ?)",
            (role, content, timestamp),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error saving text to DB: {e}")
    finally:
        if conn:
            conn.close()

def save_reply(user_text: str, reply: str):
    """
    儲存一段完整對話：先把使用者輸入存為 user，
    再把助理回覆存為 assistant。
    """
    # 先存 user 的內容
    save_text("user", user_text)
    # 再存 assistant 的回覆
    save_text("assistant", reply)

# 可以在这里添加一个简单的测试，确保 DB_PATH 在容器内是可访问的
# print(f"DB_PATH in app/db.py is set to: {DB_PATH}")