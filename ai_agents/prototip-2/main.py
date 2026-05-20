"""
main.py
-------
FastAPI uygulamasi: HTTP + WebSocket endpoint'leri.

Neden FastAPI?
- Async destek sayesinde WebSocket baglantilari bloklama olmadan yonetilir.
- /ws endpoint'i chat mesajlarini alip agent sistemine iletir, cevabi aninda geri gonderir.
- /health endpoint'i ise sistemin ayakta olup olmadigini kontrol etmek icin kullanilir.

Neden WebSocket?
- HTTP'nin istek/yanit dongusunun aksine WebSocket kalici baglanti kurar.
- Bu, gelecekte akim (streaming) veya cok adimli agent konversasyonu icin zemin hazirlar.
"""

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import database as db
from agents import run_agent

db.create_tables()

app = FastAPI(title="AI Agent Prototipi")

FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def index():
    """Chat arayuzunu sun."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health():
    """Sistem saglik kontrolu endpoint'i."""
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket baglanti akisi (connection lifecycle):
      1. accept()        : Baglantiyi kabul et.
      2. receive_text()  : Kullanicidan mesaj bekle (loop).
      3. run_agent()     : LangGraph pipeline'ini calistir.
      4. send_text()     : Cevabi kullaniciya gonder.
      5. disconnect      : Baglanti kesilirse sessizce cik.
    """
    await websocket.accept()
    try:
        while True:
            user_message = await websocket.receive_text()
            try:
                response = await asyncio.to_thread(run_agent, user_message)
            except Exception as e:
                response = f"❌ Hata oluştu: {e}"
            await websocket.send_text(response)
    except WebSocketDisconnect:
        pass
