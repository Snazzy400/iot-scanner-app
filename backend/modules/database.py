"""
database.py — Structured SQLite database for IoT Vulnerability Scanner
Tables: scans, devices, vulnerabilities, settings
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "scans.db")


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    # ── scans ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            scan_id      TEXT PRIMARY KEY,
            target       TEXT NOT NULL,
            scanned_at   TEXT NOT NULL,
            score        INTEGER DEFAULT 0,
            device_count INTEGER DEFAULT 0,
            vuln_count   INTEGER DEFAULT 0,
            results_json TEXT
        )
    """)

    # ── devices ────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            mac          TEXT PRIMARY KEY,
            ip           TEXT,
            vendor       TEXT,
            type         TEXT,
            protocol     TEXT,
            firmware     TEXT,
            first_seen   TEXT NOT NULL,
            last_seen    TEXT NOT NULL,
            times_seen   INTEGER DEFAULT 1,
            last_status  TEXT DEFAULT 'safe'
        )
    """)

    # ── vulnerabilities ────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id      TEXT NOT NULL,
            device_mac   TEXT,
            device_ip    TEXT,
            vuln_id      TEXT,
            name         TEXT,
            severity     TEXT,
            cvss         TEXT,
            description  TEXT,
            fix          TEXT,
            detected_at  TEXT NOT NULL,
            FOREIGN KEY (scan_id) REFERENCES scans(scan_id) ON DELETE CASCADE
        )
    """)

    # ── settings ───────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Default settings
    defaults = [
        ("target_network",  "192.168.100.0/24"),
        ("scan_timeout",    "30"),
        ("max_scan_history","50"),
        ("alert_on_critical","true"),
    ]
    for key, value in defaults:
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))

    conn.commit()
    conn.close()


# ── Scans ──────────────────────────────────────────────────────────────────────

def save_scan(scan_id: str, target: str, results: dict):
    """Save a completed scan and update devices/vulnerabilities tables."""
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    # Save to scans table
    c.execute("""
        INSERT OR REPLACE INTO scans
            (scan_id, target, scanned_at, score, device_count, vuln_count, results_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_id,
        target,
        results.get("scan_time", now),
        results.get("security_score", 0),
        results.get("devices_found", 0),
        results.get("total_vulnerabilities", 0),
        json.dumps(results),
    ))

    # Enforce max history limit
    max_history = int(get_setting("max_scan_history") or 50)
    c.execute("""
        DELETE FROM scans WHERE scan_id NOT IN (
            SELECT scan_id FROM scans ORDER BY scanned_at DESC LIMIT ?
        )
    """, (max_history,))

    # Update devices and vulnerabilities tables
    for device in results.get("devices", []):
        mac = device.get("mac", "unknown")
        ip  = device.get("ip", "")

        # Upsert device
        existing = c.execute("SELECT * FROM devices WHERE mac = ?", (mac,)).fetchone()
        if existing:
            c.execute("""
                UPDATE devices SET
                    ip          = ?,
                    vendor      = ?,
                    type        = ?,
                    protocol    = ?,
                    firmware    = ?,
                    last_seen   = ?,
                    times_seen  = times_seen + 1,
                    last_status = ?
                WHERE mac = ?
            """, (
                ip,
                device.get("vendor", "Unknown"),
                device.get("type", "Unknown"),
                device.get("protocol", "Unknown"),
                device.get("firmware", "Unknown"),
                now,
                device.get("status", "safe"),
                mac,
            ))
        else:
            c.execute("""
                INSERT INTO devices
                    (mac, ip, vendor, type, protocol, firmware, first_seen, last_seen, times_seen, last_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                mac,
                ip,
                device.get("vendor", "Unknown"),
                device.get("type", "Unknown"),
                device.get("protocol", "Unknown"),
                device.get("firmware", "Unknown"),
                now,
                now,
                device.get("status", "safe"),
            ))

        # Save vulnerabilities
        for vuln in device.get("vulnerabilities", []):
            c.execute("""
                INSERT INTO vulnerabilities
                    (scan_id, device_mac, device_ip, vuln_id, name, severity, cvss, description, fix, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id,
                mac,
                ip,
                vuln.get("id", ""),
                vuln.get("name", ""),
                vuln.get("severity", "low"),
                str(vuln.get("cvss", "N/A")),
                vuln.get("desc", ""),
                vuln.get("fix", ""),
                now,
            ))

    conn.commit()
    conn.close()


def get_all_scans():
    conn = get_conn()
    rows = conn.execute(
        "SELECT scan_id, target, scanned_at, score, device_count, vuln_count FROM scans ORDER BY scanned_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_scan(scan_id: str):
    conn = get_conn()
    row = conn.execute("SELECT results_json FROM scans WHERE scan_id = ?", (scan_id,)).fetchone()
    conn.close()
    if row:
        return json.loads(row["results_json"])
    return None


def delete_scan(scan_id: str):
    conn = get_conn()
    conn.execute("DELETE FROM scans WHERE scan_id = ?", (scan_id,))
    conn.execute("DELETE FROM vulnerabilities WHERE scan_id = ?", (scan_id,))
    conn.commit()
    conn.close()


def delete_all_scans():
    conn = get_conn()
    conn.execute("DELETE FROM scans")
    conn.execute("DELETE FROM vulnerabilities")
    conn.commit()
    conn.close()


# ── Devices ───────────────────────────────────────────────────────────────────

def get_all_devices():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM devices ORDER BY last_seen DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_device(mac: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM devices WHERE mac = ?", (mac,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_device(mac: str):
    conn = get_conn()
    conn.execute("DELETE FROM devices WHERE mac = ?", (mac,))
    conn.commit()
    conn.close()


# ── Vulnerabilities ───────────────────────────────────────────────────────────

def get_all_vulnerabilities(severity: str = None, limit: int = 100):
    conn = get_conn()
    if severity:
        rows = conn.execute(
            "SELECT * FROM vulnerabilities WHERE severity = ? ORDER BY detected_at DESC LIMIT ?",
            (severity, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM vulnerabilities ORDER BY detected_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_vuln_stats():
    """Get vulnerability counts grouped by severity."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT severity, COUNT(*) as count
        FROM vulnerabilities
        GROUP BY severity
    """).fetchall()
    conn.close()
    return {r["severity"]: r["count"] for r in rows}


def get_device_vuln_history(mac: str):
    """Get all vulnerabilities ever found for a specific device."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT v.*, s.scanned_at FROM vulnerabilities v
        JOIN scans s ON v.scan_id = s.scan_id
        WHERE v.device_mac = ?
        ORDER BY s.scanned_at DESC
    """, (mac,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Settings ──────────────────────────────────────────────────────────────────

def get_setting(key: str):
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None


def update_setting(key: str, value: str):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def get_all_settings():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM settings").fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_dashboard_stats():
    """Summary stats for the database tab."""
    conn = get_conn()

    total_scans    = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
    total_devices  = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    total_vulns    = conn.execute("SELECT COUNT(*) FROM vulnerabilities").fetchone()[0]
    avg_score      = conn.execute("SELECT AVG(score) FROM scans").fetchone()[0]

    # Most vulnerable device
    most_vuln = conn.execute("""
        SELECT device_ip, device_mac, COUNT(*) as count
        FROM vulnerabilities
        GROUP BY device_mac
        ORDER BY count DESC LIMIT 1
    """).fetchone()

    # Severity breakdown
    sev_rows = conn.execute("""
        SELECT severity, COUNT(*) as count FROM vulnerabilities GROUP BY severity
    """).fetchall()

    # Score trend (last 10 scans)
    score_trend = conn.execute("""
        SELECT scanned_at, score FROM scans ORDER BY scanned_at DESC LIMIT 10
    """).fetchall()

    conn.close()

    return {
        "total_scans":   total_scans,
        "total_devices": total_devices,
        "total_vulns":   total_vulns,
        "avg_score":     round(avg_score or 0, 1),
        "most_vulnerable_device": dict(most_vuln) if most_vuln else None,
        "severity_breakdown": {r["severity"]: r["count"] for r in sev_rows},
        "score_trend": [{"date": r["scanned_at"][:10], "score": r["score"]} for r in reversed(score_trend)],
    }


# Init on import
init_db()
