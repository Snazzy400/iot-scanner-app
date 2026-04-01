"""
main.py — IoT Vulnerability Scanner API
Author: Nasir Aliyu | NEU/22/23/CYB/00078
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from modules.scanner import run_scan
from modules.database import (
    init_db, save_scan, get_all_scans, get_scan, delete_scan, delete_all_scans,
    get_all_devices, get_device, delete_device,
    get_all_vulnerabilities, get_vuln_stats, get_device_vuln_history,
    get_all_settings, update_setting, get_dashboard_stats,
)

app = FastAPI(title="IoT Vulnerability Scanner", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory scan status store
scan_jobs = {}

init_db()


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "running", "service": "IoT Vulnerability Scanner", "version": "1.0.0"}


# ── Scanning ──────────────────────────────────────────────────────────────────

@app.post("/api/scan/start")
async def start_scan(background_tasks: BackgroundTasks, target: str = "192.168.100.0/24"):
    scan_id = str(uuid.uuid4())
    scan_jobs[scan_id] = {"status": "running", "progress": 0, "stage": "Initializing..."}
    background_tasks.add_task(do_scan, scan_id, target)
    return {"scan_id": scan_id}


async def do_scan(scan_id: str, target: str):
    def update(stage: str, progress: float):
        scan_jobs[scan_id].update({"stage": stage, "progress": progress})

    try:
        results = await run_scan(target, update)
        save_scan(scan_id, target, results)
        scan_jobs[scan_id] = {"status": "complete", "progress": 100, "results": results}
    except Exception as e:
        scan_jobs[scan_id] = {"status": "error", "error": str(e)}


@app.get("/api/scan/status/{scan_id}")
def scan_status(scan_id: str):
    return scan_jobs.get(scan_id, {"status": "not_found"})


# ── Scans ──────────────────────────────────────────────────────────────────

@app.get("/api/scans")
def list_scans():
    return get_all_scans()


@app.get("/api/scans/{scan_id}")
def get_scan_result(scan_id: str):
    data = get_scan(scan_id)
    if not data:
        return {"error": "Scan not found"}
    return data


@app.delete("/api/scans/{scan_id}")
def remove_scan(scan_id: str):
    delete_scan(scan_id)
    return {"deleted": scan_id}


@app.delete("/api/scans")
def remove_all_scans():
    delete_all_scans()
    return {"deleted": "all"}


# ── Devices ───────────────────────────────────────────────────────────────────

@app.get("/api/devices")
def list_devices():
    return get_all_devices()


@app.get("/api/devices/{mac}")
def get_device_detail(mac: str):
    device = get_device(mac)
    if not device:
        return {"error": "Device not found"}
    history = get_device_vuln_history(mac)
    return {**device, "vulnerability_history": history}


@app.delete("/api/devices/{mac}")
def remove_device(mac: str):
    delete_device(mac)
    return {"deleted": mac}


# ── Vulnerabilities ───────────────────────────────────────────────────────────

@app.get("/api/vulnerabilities")
def list_vulnerabilities(severity: str = None, limit: int = 100):
    return get_all_vulnerabilities(severity=severity, limit=limit)


@app.get("/api/vulnerabilities/stats")
def vuln_stats():
    return get_vuln_stats()


# ── Settings ──────────────────────────────────────────────────────────────────

@app.get("/api/settings")
def list_settings():
    return get_all_settings()


@app.put("/api/settings/{key}")
def set_setting(key: str, value: str):
    update_setting(key, value)
    return {"key": key, "value": value}


# ── Dashboard Stats ───────────────────────────────────────────────────────────

@app.get("/api/stats")
def dashboard_stats():
    return get_dashboard_stats()


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
