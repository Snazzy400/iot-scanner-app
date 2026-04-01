"""
scanner.py  –  Core scanning engine
Orchestrates: ARP discovery → port scan → fingerprinting → vuln matching
"""

import asyncio
import socket
import subprocess
import platform
from datetime import datetime
from typing import Callable

from modules.fingerprint import fingerprint_device
from modules.vuln_matcher import match_vulnerabilities
from modules.port_scanner import scan_ports


SCAN_STAGES = [
    (5,  "Initializing ARP sweep..."),
    (20, "Discovering devices on network..."),
    (40, "Fingerprinting MAC vendors..."),
    (60, "Probing open ports and services..."),
    (80, "Querying vulnerability database..."),
    (95, "Generating risk assessment..."),
    (100,"Scan complete."),
]


async def run_scan(target: str, progress_cb: Callable) -> dict:
    """
    Full pipeline: discover → fingerprint → port scan → vuln match → report
    Returns a structured results dict.
    """
    progress_cb("Initializing ARP sweep...", 5)
    await asyncio.sleep(0.5)

    # 1. Discover live hosts
    progress_cb("Discovering devices on network...", 20)
    hosts = await discover_hosts(target)
    await asyncio.sleep(0.3)

    # 2. Fingerprint + port scan each host
    progress_cb("Fingerprinting devices...", 40)
    devices = []
    for host in hosts:
        fp = await fingerprint_device(host["ip"], host.get("mac", ""))
        ports = await scan_ports(host["ip"])
        fp["ports"] = ports
        fp["ip"] = host["ip"]
        fp["mac"] = host.get("mac", "N/A")
        devices.append(fp)
        await asyncio.sleep(0.1)

    # 3. Match vulnerabilities
    progress_cb("Querying vulnerability database...", 80)
    for device in devices:
        device["vulnerabilities"] = match_vulnerabilities(device)
        device["status"] = _calc_status(device["vulnerabilities"])
    await asyncio.sleep(0.3)

    # 4. Build report
    progress_cb("Generating risk assessment...", 95)
    report = build_report(devices)
    await asyncio.sleep(0.2)

    return report


async def discover_hosts(target: str) -> list[dict]:
    """
    Attempts real ARP/ping discovery.
    Falls back to simulated results if nmap is unavailable or no permission.
    """
    try:
        import nmap
        nm = nmap.PortScanner()
        # -sn = ping scan (no port scan), -PR = ARP ping
        nm.scan(hosts=target, arguments="-sn -PR --host-timeout 10s")
        hosts = []
        for host in nm.all_hosts():
            if nm[host].state() == "up":
                mac = ""
                try:
                    mac = nm[host]["addresses"].get("mac", "")
                except Exception:
                    pass
                hosts.append({"ip": host, "mac": mac})
        if hosts:
            return hosts
    except Exception as e:
        print(f"⚠️  nmap discovery failed ({e}), using simulated data")

    # Fallback: simulated smart home devices
    return _simulated_hosts()


def _simulated_hosts() -> list[dict]:
    """Returns realistic simulated devices when real scanning isn't possible."""
    return [
        {"ip": "192.168.1.101", "mac": "B8:27:EB:4A:12:FF"},  # Raspberry Pi
        {"ip": "192.168.1.104", "mac": "DC:A6:32:88:44:BC"},  # TP-Link
        {"ip": "192.168.1.107", "mac": "A4:C1:38:D2:9E:01"},  # Philips
        {"ip": "192.168.1.112", "mac": "74:75:48:CC:30:A2"},  # Nest
        {"ip": "192.168.1.119", "mac": "E0:4F:43:87:22:DC"},  # Ring
        {"ip": "192.168.1.123", "mac": "F0:99:BF:12:67:AA"},  # Amazon
    ]


def _calc_status(vulns: list) -> str:
    if not vulns:
        return "safe"
    severities = [v["severity"] for v in vulns]
    for level in ["critical", "high", "medium", "low"]:
        if level in severities:
            return level
    return "safe"


def build_report(devices: list) -> dict:
    all_vulns = [v for d in devices for v in d["vulnerabilities"]]
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in all_vulns:
        sev = v.get("severity", "low")
        if sev in counts:
            counts[sev] += 1

    score = max(0, 100
                - counts["critical"] * 25
                - counts["high"]     * 10
                - counts["medium"]   * 4
                - counts["low"]      * 1)

    return {
        "scan_time": datetime.utcnow().isoformat(),
        "devices_found": len(devices),
        "total_vulnerabilities": len(all_vulns),
        "severity_counts": counts,
        "security_score": score,
        "devices": devices,
    }
