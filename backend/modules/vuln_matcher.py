"""
vuln_matcher.py  –  Maps device fingerprint + open ports → known CVEs
IoT-specific vulnerability knowledge base (aligned with project Chapter 2)
"""

from modules.vuln_db import VULNERABILITY_DB


def match_vulnerabilities(device: dict) -> list[dict]:
    """
    Given a fingerprinted device dict, return a list of matched vulnerabilities.
    Matching logic:
      1. Device-type rules  (e.g. all Smart Plugs get checked for UPnP CVE)
      2. Protocol rules     (e.g. ZigBee replay, MQTT unencrypted)
      3. Port-presence rules(e.g. port 23 open → Telnet enabled)
      4. Firmware version rules
    """
    matched = []
    open_ports = {p["port"] for p in device.get("ports", [])}
    device_type = device.get("type", "").lower()
    protocol = device.get("protocol", "").lower()
    vendor = device.get("vendor", "").lower()
    firmware = device.get("firmware", "")

    for vuln in VULNERABILITY_DB:
        if _matches(vuln, device_type, protocol, vendor, open_ports, firmware):
            matched.append({
                "id":       vuln["id"],
                "name":     vuln["name"],
                "severity": vuln["severity"],
                "desc":     vuln["desc"],
                "fix":      vuln["fix"],
                "cvss":     vuln.get("cvss", "N/A"),
            })

    return matched


def _matches(vuln, device_type, protocol, vendor, open_ports, firmware) -> bool:
    rules = vuln.get("match", {})

    # All rules in a match block must pass (AND logic)
    if "device_types" in rules:
        if not any(t in device_type for t in rules["device_types"]):
            return False

    if "protocols" in rules:
        if not any(p in protocol for p in rules["protocols"]):
            return False

    if "vendors" in rules:
        if not any(v in vendor for v in rules["vendors"]):
            return False

    if "ports_open" in rules:
        if not any(p in open_ports for p in rules["ports_open"]):
            return False

    if "ports_absent" in rules:
        # Flag if a SECURE port is absent (e.g. 443 absent means no HTTPS)
        if any(p in open_ports for p in rules["ports_absent"]):
            return False  # secure alternative IS present, skip

    if "firmware_below" in rules:
        if not _firmware_older_than(firmware, rules["firmware_below"]):
            return False

    return True


def _firmware_older_than(current: str, threshold: str) -> bool:
    """Simple version comparison. Returns True if current < threshold."""
    try:
        def parse(v):
            return [int(x) for x in v.lstrip("v").split("-")[0].split(".") if x.isdigit()]
        return parse(current) < parse(threshold)
    except Exception:
        return False
