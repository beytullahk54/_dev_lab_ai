"""
database.py
-----------
SQLite veritaban? ba?lant?s? ve CRUD i?lemleri.

Neden bu yap??
- sqlite3 Python'da yerle?ik gelir, ekstra kurulum gerekmez.
- Tek bir .db dosyas?nda t?m veriler tutulur; geli?tirme/prototip i?in idealdi.
- Tablolar uygulama ilk ba?lad???nda otomatik olu?turulur (create_tables).
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def get_connection() -> sqlite3.Connection:
    """Her ?a?r?da yeni bir ba?lant? d?nd?r?r (thread-safe)."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # s?tun ismiyle eri?im i?in
    return conn


def create_tables() -> None:
    """Uygulama ba?lang?c?nda ?al???r; tablo yoksa olu?turur."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def insert_user(name: str) -> dict:
    """
    Yeni kullan?c? ekler.
    - Ayn? isim zaten varsa bilgi mesaj? d?nd?r?r (hata f?rlatmaz).
    - Returns: {"status": "created"|"exists", "name": name}
    """
    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
            conn.commit()
        return {"status": "created", "name": name}
    except sqlite3.IntegrityError:
        return {"status": "exists", "name": name}


def count_users() -> int:
    """Toplam kullan?c? say?s?n? d?nd?r?r."""
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM users").fetchone()
    return row["total"]
