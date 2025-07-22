# service/llm/llm_openai.py

import os, traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import openai # 确保 openai 库已安装

app = FastAPI()
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/") # 这是独立服务，路径是 /
async def chat(request: Request):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="Missing OPENAI_API_KEY. Please check .env file and docker-compose.yml.")

    body = await request.json()
    user_text = body.get("text", "")
    print(f"LLM service received text: {user_text}")

    if not user_text:
        raise HTTPException(status_code=400, detail="Missing 'text' in request body.")

    try:
        # 确保您有权限使用此模型，否则请更改为 "gpt-3.5-turbo"
        resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_text}]
        )
        reply = resp.choices[0].message.content
        print(f"LLM generated reply: {reply}")
    except openai.error.AuthenticationError as e:
        print(f"OpenAI Authentication Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid OpenAI API Key. Please check your OPENAI_API_KEY.")
    except openai.error.PermissionError as e:
        print(f"OpenAI Permission Error: {e}")
        raise HTTPException(status_code=403, detail=f"API Key lacks permission for 'gpt-4' model. Try 'gpt-3.5-turbo' or check your OpenAI plan. Error: {e}")
    except Exception as e:
        tb = traceback.format_exc()
        print("=== LLM ERROR TRACE ===\n", tb)
        raise HTTPException(status_code=502, detail=f"LLM service error: {e}. Check LLM service logs for more details.")

    # LLM 服务只返回 AI 回复，不直接操作数据库
    return JSONResponse({"reply": reply})


