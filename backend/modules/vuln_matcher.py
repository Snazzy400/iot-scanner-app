"""
vuln_matcher.py — Matches device profiles against the vulnerability knowledge base
"""

from modules.vuln_db import VULNERABILITY_DB


def match_vulnerabilities(device: dict) -> list:
    """
    Match a device profile against vulnerability rules.
    Only returns vulnerabilities where ALL conditions are satisfied.
    """
    matched = []
    open_ports   = [p["port"] for p in device.get("ports", [])]
    vendor       = device.get("vendor", "").lower()
    device_type  = device.get("type", "").lower()
    protocol     = device.get("protocol", "").lower()
    firmware     = device.get("firmware", "Unknown")

    for rule in VULNERABILITY_DB:
        conditions = rule.get("conditions", {})
        match = True

        # ── ports_open: ALL listed ports must be open ──────────────────
        if "ports_open" in conditions:
            if not any(p in open_ports for p in conditions["ports_open"]):
                match = False

        # ── ports_absent: listed ports must NOT be open ────────────────
        if "ports_absent" in conditions and match:
            if any(p in open_ports for p in conditions["ports_absent"]):
                match = False

        # ── vendors: device vendor must match ─────────────────────────
        if "vendors" in conditions and match:
            if not any(v.lower() in vendor for v in conditions["vendors"]):
                match = False

        # ── device_types: device type must match ──────────────────────
        if "device_types" in conditions and match:
            if not any(t.lower() in device_type for t in conditions["device_types"]):
                match = False

        # ── protocols: device protocol must match ─────────────────────
        if "protocols" in conditions and match:
            if not any(p.lower() in protocol for p in conditions["protocols"]):
                match = False

        # ── firmware_below: firmware version must be below threshold ───
        if "firmware_below" in conditions and match:
            if firmware == "Unknown":
                match = False
            else:
                try:
                    fw_parts    = [int(x) for x in firmware.split(".")[:2]]
                    limit_parts = [int(x) for x in conditions["firmware_below"].split(".")[:2]]
                    match = fw_parts < limit_parts
                except Exception:
                    match = False

        if match:
            matched.append({
                "id":       rule["id"],
                "name":     rule["name"],
                "severity": rule["severity"],
                "cvss":     rule.get("cvss", "N/A"),
                "desc":     rule["desc"],
                "fix":      rule["fix"],
            })

    return matched


def get_device_status(vulnerabilities: list) -> str:
    """Return the highest severity level found."""
    if not vulnerabilities:
        return "safe"
    order = ["critical", "high", "medium", "low"]
    for level in order:
        if any(v["severity"] == level for v in vulnerabilities):
            return level
    return "safe"
