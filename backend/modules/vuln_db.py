# ── New Tuya/CozyLife and eWeLink vulnerability rules to add to vuln_db.py ──

TUYA_EWELINK_RULES = [
    {
        "id": "IOT-TUYA-001",
        "name": "Tuya Unencrypted Local API (Port 6668)",
        "severity": "high",
        "cvss": "7.1",
        "desc": "Tuya-based devices expose a local control API on port 6668 using AES-ECB encryption with a hardcoded or easily extractable local key. This allows attackers on the same network to intercept and replay device commands.",
        "fix": "Disable local API if not required. Use Tuya's encrypted cloud control mode and isolate IoT devices on a separate VLAN.",
        "conditions": {
            "vendors": ["CozyLife", "Tuya"],
            "ports_open": [6668],
        }
    },
    {
        "id": "IOT-TUYA-002",
        "name": "Tuya SmartConfig Credential Exposure",
        "severity": "medium",
        "cvss": "5.9",
        "desc": "During device provisioning, Tuya devices use the SmartConfig protocol which broadcasts the Wi-Fi SSID and password in UDP packets. An attacker within radio range can capture these packets and extract network credentials.",
        "fix": "Use AP mode provisioning instead of SmartConfig. Avoid provisioning devices on public or shared networks.",
        "conditions": {
            "vendors": ["CozyLife", "Tuya"],
            "device_types": ["Smart Plug", "Smart Bulb"],
        }
    },
    {
        "id": "IOT-EWELINK-001",
        "name": "eWeLink Unencrypted WebSocket Communication",
        "severity": "high",
        "cvss": "7.4",
        "desc": "eWeLink devices communicate with their cloud servers over WebSocket connections that may fall back to unencrypted channels. Device state and control commands can be intercepted by a man-in-the-middle attacker.",
        "fix": "Ensure firmware is updated to the latest version which enforces TLS for all WebSocket communications. Monitor for unencrypted traffic on port 8080.",
        "conditions": {
            "vendors": ["QIACHIP", "eWeLink"],
            "ports_open": [8080],
        }
    },
    {
        "id": "IOT-EWELINK-002",
        "name": "eWeLink Default Device Key",
        "severity": "critical",
        "cvss": "9.1",
        "desc": "Early eWeLink firmware versions used a default or easily guessable device key for local LAN control. This allows any device on the same network to send unauthorised control commands to the smart device.",
        "fix": "Update device firmware through the eWeLink app. Enable LAN control only when required and segment IoT devices from the main network.",
        "conditions": {
            "vendors": ["QIACHIP", "eWeLink"],
            "device_types": ["Smart Bulb", "Smart Plug"],
        }
    },
    {
        "id": "IOT-TUYA-003",
        "name": "Insecure Firmware Over-the-Air (OTA) Update",
        "severity": "medium",
        "cvss": "6.5",
        "desc": "Some Tuya and eWeLink based devices do not verify the cryptographic signature of OTA firmware updates. This could allow an attacker with network access to push malicious firmware to the device.",
        "fix": "Keep device firmware updated through the official app. Use network segmentation to prevent unauthorised devices from reaching the IoT network.",
        "conditions": {
            "vendors": ["CozyLife", "Tuya", "QIACHIP", "eWeLink"],
            "device_types": ["Smart Plug", "Smart Bulb"],
        }
    },
]
