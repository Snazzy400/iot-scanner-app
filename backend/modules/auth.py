"""
auth.py — Authentication module for IoT Vulnerability Scanner
Handles password hashing, JWT token creation and verification
"""

import sqlite3
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

# ── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY  = "iot-scanner-secret-key-nasir-neu-2024-change-in-production"
ALGORITHM   = "HS256"
TOKEN_EXPIRE_HOURS = 8

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scans.db")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── DB Setup ──────────────────────────────────────────────────────────────────
def init_auth_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    # Create default admin if no users exist
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        hashed = pwd_ctx.hash("admin123")
        conn.execute(
            "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
            ("admin", hashed, datetime.utcnow().isoformat())
        )
        print("✅ Default admin created: username=admin, password=admin123")
    conn.commit()
    conn.close()


# ── Password ──────────────────────────────────────────────────────────────────
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)


# ── User lookup ───────────────────────────────────────────────────────────────
def get_user(username: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


# ── JWT ───────────────────────────────────────────────────────────────────────
def create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        return get_user(username)
    except JWTError:
        return None


# ── Change password ───────────────────────────────────────────────────────────
def change_password(username: str, new_password: str):
    hashed = hash_password(new_password)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, username))
    conn.commit()
    conn.close()
