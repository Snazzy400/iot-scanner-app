"""
main.py — IoT Vulnerability Scanner API
Author: Nasir Aliyu | NEU/22/23/CYB/00078
"""

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import uuid

from modules.scanner import run_scan
from modules.database import (
    init_db, save_scan, get_all_scans, get_scan, delete_scan, delete_all_scans,
    get_all_devices, get_device, delete_device,
    get_all_vulnerabilities, get_vuln_stats, get_device_vuln_history,
    get_all_settings, update_setting, get_dashboard_stats,
)
from modules.auth import init_auth_db, authenticate_user, create_token, verify_token, change_password

app = FastAPI(title="IoT Vulnerability Scanner", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
scan_jobs = {}

init_db()
init_auth_db()


# ── Auth helpers ──────────────────────────────────────────────────────────────

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


# ── Auth endpoints ────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(req.username)
    return {"access_token": token, "token_type": "bearer", "username": req.username}

@app.get("/api/auth/me")
def get_me(user=Depends(get_current_user)):
    return {"username": user["username"], "created_at": user["created_at"]}

@app.post("/api/auth/change-password")
def change_pwd(req: ChangePasswordRequest, user=Depends(get_current_user)):
    if not authenticate_user(user["username"], req.current_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    change_password(user["username"], req.new_password)
    return {"message": "Password changed successfully"}


# ── Health (public) ───────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "running", "service": "IoT Vulnerability Scanner", "version": "1.0.0"}


# ── Scanning (protected) ──────────────────────────────────────────────────────

@app.post("/api/scan/start")
async def start_scan(background_tasks: BackgroundTasks, target: str = "192.168.100.0/24", user=Depends(get_current_user)):
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
def scan_status(scan_id: str, user=Depends(get_current_user)):
    return scan_jobs.get(scan_id, {"status": "not_found"})


# ── Scans (protected) ─────────────────────────────────────────────────────────

@app.get("/api/scans")
def list_scans(user=Depends(get_current_user)):
    return get_all_scans()

@app.get("/api/scans/{scan_id}")
def get_scan_result(scan_id: str, user=Depends(get_current_user)):
    data = get_scan(scan_id)
    return data if data else {"error": "Scan not found"}

@app.delete("/api/scans/{scan_id}")
def remove_scan(scan_id: str, user=Depends(get_current_user)):
    delete_scan(scan_id)
    return {"deleted": scan_id}

@app.delete("/api/scans")
def remove_all_scans(user=Depends(get_current_user)):
    delete_all_scans()
    return {"deleted": "all"}


# ── Devices (protected) ───────────────────────────────────────────────────────

@app.get("/api/devices")
def list_devices(user=Depends(get_current_user)):
    return get_all_devices()

@app.get("/api/devices/{mac}")
def get_device_detail(mac: str, user=Depends(get_current_user)):
    device = get_device(mac)
    if not device:
        return {"error": "Device not found"}
    return {**device, "vulnerability_history": get_device_vuln_history(mac)}

@app.delete("/api/devices/{mac}")
def remove_device(mac: str, user=Depends(get_current_user)):
    delete_device(mac)
    return {"deleted": mac}


# ── Vulnerabilities (protected) ───────────────────────────────────────────────

@app.get("/api/vulnerabilities")
def list_vulnerabilities(severity: str = None, limit: int = 100, user=Depends(get_current_user)):
    return get_all_vulnerabilities(severity=severity, limit=limit)

@app.get("/api/vulnerabilities/stats")
def vuln_stats(user=Depends(get_current_user)):
    return get_vuln_stats()


# ── Settings (protected) ──────────────────────────────────────────────────────

@app.get("/api/settings")
def list_settings(user=Depends(get_current_user)):
    return get_all_settings()

@app.put("/api/settings/{key}")
def set_setting(key: str, value: str, user=Depends(get_current_user)):
    update_setting(key, value)
    return {"key": key, "value": value}


# ── Stats (protected) ─────────────────────────────────────────────────────────

@app.get("/api/stats")
def dashboard_stats(user=Depends(get_current_user)):
    return get_dashboard_stats()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
