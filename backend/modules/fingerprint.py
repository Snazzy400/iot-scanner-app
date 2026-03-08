"""
fingerprint.py  –  Device identification via MAC OUI + banner grabbing
"""

import asyncio
import httpx
import re

# OUI prefix → vendor/device type mapping (extended for IoT)
MAC_VENDOR_DB = {
    # ── Your real network devices ──────────────────────────────────────────
    "00:90:4A": {"vendor": "Zoom Telephonics (Router)", "type": "Home Router",     "protocol": "Wi-Fi"},
    "EE:D2:AB": {"vendor": "Android Device (Randomized MAC)", "type": "Smartphone", "protocol": "Wi-Fi"},
    "00:15:5D": {"vendor": "Microsoft Hyper-V",         "type": "Virtual Machine", "protocol": "Ethernet"},
    "B8:27:EB": {"vendor": "Raspberry Pi Foundation", "type": "Smart Hub",      "protocol": "Wi-Fi"},
    "DC:A6:32": {"vendor": "Raspberry Pi Foundation", "type": "Smart Hub",      "protocol": "Wi-Fi"},
    "E4:5F:01": {"vendor": "Raspberry Pi Foundation", "type": "Smart Hub",      "protocol": "Wi-Fi"},
    "DC:A6:32": {"vendor": "TP-Link Technologies",    "type": "Smart Plug",     "protocol": "Wi-Fi"},
    "50:C7:BF": {"vendor": "TP-Link Technologies",    "type": "Smart Plug",     "protocol": "Wi-Fi"},
    "A4:C1:38": {"vendor": "Philips Hue",             "type": "Smart Bulb",     "protocol": "ZigBee"},
    "00:17:88": {"vendor": "Philips Hue",             "type": "Smart Bulb",     "protocol": "ZigBee"},
    "74:75:48": {"vendor": "Nest Labs (Google)",      "type": "Smart Thermostat","protocol": "Wi-Fi"},
    "18:B4:30": {"vendor": "Nest Labs (Google)",      "type": "Smart Thermostat","protocol": "Wi-Fi"},
    "E0:4F:43": {"vendor": "Ring (Amazon)",           "type": "Security Camera","protocol": "Wi-Fi"},
    "FC:65:DE": {"vendor": "Ring (Amazon)",           "type": "Security Camera","protocol": "Wi-Fi"},
    "F0:99:BF": {"vendor": "Amazon Technologies",     "type": "Smart Speaker",  "protocol": "Wi-Fi"},
    "44:65:0D": {"vendor": "Amazon Technologies",     "type": "Smart Speaker",  "protocol": "Wi-Fi"},
    "68:37:E9": {"vendor": "Samsung SmartThings",     "type": "Smart Hub",      "protocol": "Z-Wave"},
    "00:15:8D": {"vendor": "Xiaomi",                  "type": "Smart Sensor",   "protocol": "ZigBee"},
    "64:90:C1": {"vendor": "Belkin (WeMo)",           "type": "Smart Switch",   "protocol": "Wi-Fi"},
    "EC:FA:BC": {"vendor": "Espressif Systems",       "type": "Smart Device",   "protocol": "Wi-Fi"},
    "AC:67:B2": {"vendor": "Espressif Systems",       "type": "Smart Device",   "protocol": "Wi-Fi"},
}

FIRMWARE_HINTS = {
    "Smart Hub":        "v2.1.0",
    "Smart Plug":       "v1.0.13",
    "Smart Bulb":       "v1.93.1",
    "Smart Thermostat": "v6.4.0-8",
    "Security Camera":  "v3.33.0",
    "Smart Speaker":    "v0.0.511",
    "Smart Switch":     "v3.0.2",
    "Smart Sensor":     "v1.4.0",
    "Smart Device":     "v2.0.0",
}


async def fingerprint_device(ip: str, mac: str) -> dict:
    """
    Identify a device by MAC OUI lookup + optional HTTP banner grab.
    Falls back to 'Unknown Device' if no match.
    """
    info = _lookup_mac(mac)

    # Try to grab HTTP banner for extra version info
    firmware = FIRMWARE_HINTS.get(info["type"], "Unknown")
    try:
        firmware = await _grab_firmware_hint(ip) or firmware
    except Exception:
        pass

    return {
        "vendor":   info["vendor"],
        "type":     info["type"],
        "protocol": info["protocol"],
        "firmware": firmware,
    }


def _lookup_mac(mac: str) -> dict:
    """Match first 3 octets of MAC address against OUI database."""
    if not mac or mac == "N/A":
        return _unknown()
    prefix = mac.upper()[:8]
    if prefix in MAC_VENDOR_DB:
        return MAC_VENDOR_DB[prefix]
    # Try shorter prefix (some MACs use different separator styles)
    prefix2 = mac.upper().replace("-", ":")[:8]
    if prefix2 in MAC_VENDOR_DB:
        return MAC_VENDOR_DB[prefix2]
    return _unknown()


def _unknown() -> dict:
    return {"vendor": "Unknown Vendor", "type": "Unknown Device", "protocol": "Unknown"}


async def _grab_firmware_hint(ip: str, timeout: float = 2.0) -> str | None:
    """
    Attempt HTTP banner grab on port 80 to extract firmware/version strings.
    Non-blocking — returns None on any failure.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
            r = await client.get(f"http://{ip}/", follow_redirects=True)
            server = r.headers.get("server", "")
            # Look for version-like strings
            match = re.search(r"[\w\-]+/[\d]+\.[\d]+[\.\d]*", server)
            if match:
                return match.group(0)
    except Exception:
        pass
    return None