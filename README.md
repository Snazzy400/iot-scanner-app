# IoT Vulnerability Scanner
**Nasir Aliyu — NEU/22/23/CYB/00078**  
Design and Implementation of IoT Vulnerability Scanner for Smart Home Devices

---

## Project Structure

```
iot-scanner/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── requirements.txt
│   ├── data/                    ← SQLite database (auto-created)
│   └── modules/
│       ├── scanner.py           ← Scan orchestrator
│       ├── fingerprint.py       ← MAC OUI + banner grabbing
│       ├── port_scanner.py      ← TCP port scanning
│       ├── vuln_matcher.py      ← CVE matching engine
│       ├── vuln_db.py           ← IoT vulnerability knowledge base
│       └── database.py          ← SQLite persistence
└── frontend/
    └── src/
        └── App.jsx              ← React dashboard (connects to backend)
```

---

## Setup Instructions

### 1. Backend

**Prerequisites:** Python 3.10+, pip

```bash
cd backend
pip install -r requirements.txt
```

**Run the API:**
```bash
python main.py
```
The API will be available at: `http://localhost:8000`

**API Documentation (auto-generated):**  
Open `http://localhost:8000/docs` in your browser.

---

### 2. Frontend

**Prerequisites:** Node.js 18+

The frontend (`App.jsx`) is a React component. To run it:

**Option A — Use with Vite (recommended)**
```bash
cd frontend
npm create vite@latest . -- --template react
# Replace src/App.jsx with the provided App.jsx
npm install
npm run dev
```

**Option B — Paste into Claude.ai artifact**  
Copy `frontend/src/App.jsx` content directly into a Claude artifact.

---

## API Endpoints

| Method | Endpoint                    | Description                        |
|--------|-----------------------------|------------------------------------|
| POST   | `/api/scan/start`           | Start a new scan (returns scan_id) |
| GET    | `/api/scan/status/{id}`     | Poll scan progress                 |
| GET    | `/api/scan/results/{id}`    | Get full scan results              |
| GET    | `/api/scans`                | List all past scans                |
| GET    | `/api/scans/{id}`           | Get a specific past scan           |
| GET    | `/docs`                     | Interactive API documentation      |

---

## Scanning Behaviour

The scanner operates in two modes:

**Real Mode** (requires nmap + admin/root privileges):
- ARP ping sweep to discover live hosts
- TCP port scan across IoT-relevant ports
- HTTP banner grabbing for firmware hints

**Simulation Mode** (no nmap / no elevated privileges):
- Uses realistic simulated smart home device set
- Full vulnerability matching still runs against the knowledge base
- Useful for development, demos, and academic evaluation

To enable real scanning on Windows:
```bash
# Run terminal as Administrator
python main.py
```

On Linux/macOS:
```bash
sudo python main.py
```

---

## Vulnerability Knowledge Base

Located in `modules/vuln_db.py`. Each entry contains:
- CVE ID or internal identifier
- Severity (critical / high / medium / low)
- CVSS score
- Description (with academic citations)
- Remediation advice
- Matching rules (device type, protocol, open ports, vendor, firmware version)

---

## Technologies Used

| Component       | Technology              |
|-----------------|-------------------------|
| Backend API     | Python / FastAPI        |
| Network Scanner | Nmap / python-nmap      |
| Packet Analysis | Scapy                   |
| HTTP Probing    | httpx (async)           |
| Database        | SQLite                  |
| Frontend        | React (JSX)             |
| Styling         | Inline CSS / Tailwind   |

---

## Academic References

This implementation is aligned with Chapter 2 & 3 of the project report:
- Costa et al. (2019) — IoT vulnerability assessment methodology
- Amro (2020) — IoT vulnerability scanning state of the art  
- Heiding et al. (2023) — Penetration testing of smart home devices
- Bakhshi et al. (2024) — IoT firmware vulnerability review
- Palo Alto Networks (2025) — IoT threat landscape report
