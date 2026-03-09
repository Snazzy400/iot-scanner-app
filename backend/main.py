"""
IoT Vulnerability Scanner - Backend API
Nasir Aliyu - NEU/22/23/CYB/00078
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import uuid
from datetime import datetime

from modules.scanner import run_full_scan
from modules.database import init_db, save_scan_result, get_all_scans, get_scan_by_id

app = FastAPI(
    title="IoT Vulnerability Scanner API",
    description="Smart Home IoT Security Assessment System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory scan job tracker
active_scans: dict = {}

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Database initialized")
    print("✅ IoT Scanner API running at http://localhost:8000")


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "running", "service": "IoT Vulnerability Scanner", "version": "1.0.0"}


# ── Scan endpoints ────────────────────────────────────────────────────────────

@app.post("/api/scan/start")
async def start_scan(background_tasks: BackgroundTasks, target: str = "192.168.100.0/24"):
    """
    Kick off a full scan in the background.
    Returns a scan_id you can poll for status/results.
    """
    scan_id = str(uuid.uuid4())
    active_scans[scan_id] = {
        "scan_id": scan_id,
        "status": "running",
        "target": target,
        "started_at": datetime.utcnow().isoformat(),
        "progress": 0,
        "stage": "Initializing..."
    }
    background_tasks.add_task(_execute_scan, scan_id, target)
    return {"scan_id": scan_id, "status": "running", "target": target}


@app.get("/api/scan/status/{scan_id}")
def scan_status(scan_id: str):
    """Poll this to track scan progress."""
    if scan_id not in active_scans:
        return JSONResponse(status_code=404, content={"error": "Scan not found"})
    return active_scans[scan_id]


@app.get("/api/scan/results/{scan_id}")
def scan_results(scan_id: str):
    """Get full results once scan is complete."""
    if scan_id not in active_scans:
        return JSONResponse(status_code=404, content={"error": "Scan not found"})
    job = active_scans[scan_id]
    if job["status"] != "complete":
        return JSONResponse(status_code=202, content={"status": job["status"], "progress": job.get("progress", 0)})
    return job


@app.get("/api/scans")
def list_scans():
    """List all past scans from the database."""
    return get_all_scans()


@app.get("/api/scans/{scan_id}")
def get_scan(scan_id: str):
    """Retrieve a specific past scan by ID."""
    result = get_scan_by_id(scan_id)
    if not result:
        return JSONResponse(status_code=404, content={"error": "Scan not found"})
    return result


# ── Background task ───────────────────────────────────────────────────────────

async def _execute_scan(scan_id: str, target: str):
    """Runs the scanner and updates the in-memory job tracker."""
    try:
        def progress_callback(stage: str, pct: int):
            active_scans[scan_id]["stage"] = stage
            active_scans[scan_id]["progress"] = pct

        results = await run_full_scan(target, progress_callback)

        active_scans[scan_id].update({
            "status": "complete",
            "progress": 100,
            "stage": "Done",
            "completed_at": datetime.utcnow().isoformat(),
            "results": results,
        })

        save_scan_result(scan_id, target, results)

    except Exception as e:
        active_scans[scan_id].update({
            "status": "error",
            "error": str(e)
        })
        print(f"❌ Scan {scan_id} failed: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
