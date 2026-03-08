"""
database.py  –  SQLite persistence layer for scan results
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scans.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id          TEXT PRIMARY KEY,
                target      TEXT NOT NULL,
                scanned_at  TEXT NOT NULL,
                score       INTEGER,
                device_count INTEGER,
                vuln_count  INTEGER,
                results_json TEXT NOT NULL
            )
        """)
    print(f"✅ SQLite DB ready at {DB_PATH}")


def save_scan_result(scan_id: str, target: str, results: dict):
    with _conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO scans
                (id, target, scanned_at, score, device_count, vuln_count, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_id,
            target,
            results.get("scan_time", datetime.utcnow().isoformat()),
            results.get("security_score", 0),
            results.get("devices_found", 0),
            results.get("total_vulnerabilities", 0),
            json.dumps(results),
        ))


def get_all_scans() -> list[dict]:
    with _conn() as conn:
        rows = conn.execute("""
            SELECT id, target, scanned_at, score, device_count, vuln_count
            FROM scans ORDER BY scanned_at DESC
        """).fetchall()
    return [
        {
            "scan_id":      r[0],
            "target":       r[1],
            "scanned_at":   r[2],
            "score":        r[3],
            "device_count": r[4],
            "vuln_count":   r[5],
        }
        for r in rows
    ]


def get_scan_by_id(scan_id: str) -> dict | None:
    with _conn() as conn:
        row = conn.execute(
            "SELECT results_json FROM scans WHERE id = ?", (scan_id,)
        ).fetchone()
    if row:
        return json.loads(row[0])
    return None


def _conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)
