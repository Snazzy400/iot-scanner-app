"""
vuln_db.py — IoT Vulnerability Knowledge Base
CVE-linked rules for smart home device assessment
"""

VULNERABILITY_DB = [

    # ── Authentication Vulnerabilities ────────────────────────────────────
    {
        "id": "IOT-CRED-001",
        "name": "Default Credentials Detected",
        "severity": "critical",
        "cvss": "9.8",
        "desc": "Device is accessible using factory default username and password combinations. Default credentials are publicly known and exploited by botnets such as Mirai.",
        "fix": "Change default credentials immediately. Use a strong, unique password of at least 12 characters.",
        "conditions": {
            "ports_open": [80, 23, 22],
            "device_types": ["Smart Hub", "Home Router", "Security Camera"],
        }
    },
    {
        "id": "CVE-2016-10372",
        "name": "Mirai Botnet Telnet Exploit",
        "severity": "critical",
        "cvss": "9.8",
        "desc": "Telnet service is running with default or weak credentials, making the device vulnerable to the Mirai botnet infection which scans for and exploits such devices at scale.",
        "fix": "Disable Telnet immediately and use SSH with key-based authentication only.",
        "conditions": {
            "ports_open": [23],
        }
    },
    {
        "id": "IOT-CAM-001",
        "name": "Unauthenticated RTSP Stream",
        "severity": "critical",
        "cvss": "9.1",
        "desc": "RTSP video stream is accessible without authentication, allowing anyone on the network to view the camera feed without credentials.",
        "fix": "Enable RTSP authentication in camera settings. Use a strong password and restrict access by IP where possible.",
        "conditions": {
            "ports_open": [554],
            "device_types": ["Security Camera"],
        }
    },

    # ── Network Communication Vulnerabilities ─────────────────────────────
    {
        "id": "IOT-NET-001",
        "name": "Unencrypted HTTP Management Interface",
        "severity": "high",
        "cvss": "7.5",
        "desc": "The device exposes its management interface over plain HTTP without TLS encryption. Credentials and commands transmitted to this interface can be intercepted by any attacker on the same network.",
        "fix": "Enable HTTPS in device settings. If HTTPS is unavailable, restrict network access to the management interface.",
        "conditions": {
            "ports_open": [80],
            "ports_absent": [443],
        }
    },
    {
        "id": "IOT-NET-002",
        "name": "Unencrypted MQTT Broker (Port 1883)",
        "severity": "high",
        "cvss": "7.4",
        "desc": "MQTT broker is running on port 1883 without TLS encryption. All IoT messages including device commands and sensor data are transmitted in plaintext and can be intercepted or injected.",
        "fix": "Migrate to MQTT over TLS on port 8883. Configure broker to reject unauthenticated connections.",
        "conditions": {
            "ports_open": [1883],
            "ports_absent": [8883],
        }
    },
    {
        "id": "IOT-NET-003",
        "name": "FTP Service Exposed",
        "severity": "high",
        "cvss": "7.5",
        "desc": "An FTP service is running on the device, transmitting credentials and file data in plaintext. FTP is an inherently insecure protocol with no encryption.",
        "fix": "Disable FTP and replace with SFTP or SCP. If file transfer is not required, close port 21.",
        "conditions": {
            "ports_open": [21],
        }
    },
    {
        "id": "IOT-NET-004",
        "name": "TR-069 Remote Management Exposed",
        "severity": "medium",
        "cvss": "6.5",
        "desc": "TR-069 (CWMP) remote management protocol is accessible on port 7547. This protocol has been historically exploited by the Mirai Aidra and Wifatch botnets to gain control of home routers.",
        "fix": "Disable TR-069 if not required by your ISP. If required, ensure it is only accessible from ISP IP ranges.",
        "conditions": {
            "ports_open": [7547],
        }
    },
    {
        "id": "IOT-NET-005",
        "name": "UPnP Service Exposed",
        "severity": "medium",
        "cvss": "5.3",
        "desc": "Universal Plug and Play (UPnP) is enabled and accessible. UPnP has no authentication mechanism and can be abused to open firewall ports or redirect network traffic.",
        "fix": "Disable UPnP on the device and router. UPnP should never be accessible from the internet.",
        "conditions": {
            "ports_open": [49152],
        }
    },

    # ── Vendor-Specific Vulnerabilities ───────────────────────────────────
    {
        "id": "CVE-2021-4045",
        "name": "TP-Link UPnP Remote Code Execution",
        "severity": "critical",
        "cvss": "9.8",
        "desc": "A critical unauthenticated remote code execution vulnerability in TP-Link Tapo C200 and related devices allows attackers to execute arbitrary commands via a malformed UPnP request.",
        "fix": "Update TP-Link firmware to the latest version immediately. Disable UPnP if not required.",
        "conditions": {
            "vendors": ["TP-Link"],
            "ports_open": [49152],
        }
    },
    {
        "id": "CVE-2023-5614",
        "name": "TP-Link Cleartext Wi-Fi PSK Disclosure",
        "severity": "high",
        "cvss": "7.5",
        "desc": "TP-Link devices running vulnerable firmware versions expose the Wi-Fi Pre-Shared Key (PSK) in cleartext through the local management API, allowing network attackers to retrieve the Wi-Fi password.",
        "fix": "Update TP-Link firmware to version 1.1.3 or later. Rotate the Wi-Fi password after applying the update.",
        "conditions": {
            "vendors": ["TP-Link"],
            "ports_open": [80],
        }
    },

    # ── Protocol Vulnerabilities ──────────────────────────────────────────
    {
        "id": "CVE-2020-6007",
        "name": "ZigBee Touchlink Replay Attack",
        "severity": "high",
        "cvss": "7.5",
        "desc": "Philips Hue and other ZigBee-based devices are vulnerable to a Touchlink commissioning replay attack, allowing a nearby attacker to take control of ZigBee bulbs and extract the network encryption key.",
        "fix": "Update Philips Hue bridge firmware. Disable Touchlink commissioning if not in use.",
        "conditions": {
            "vendors": ["Philips Hue"],
            "protocols": ["ZigBee"],
        }
    },
    {
        "id": "IOT-PROTO-002",
        "name": "ZigBee Network Key Interception",
        "severity": "high",
        "cvss": "7.4",
        "desc": "During ZigBee device joining, the network key may be transmitted in plaintext if the Trust Centre Link Key is set to the well-known default value (ZigBeeAlliance09).",
        "fix": "Configure ZigBee coordinator to use a unique Trust Centre Link Key and enable key transport encryption.",
        "conditions": {
            "protocols": ["ZigBee"],
        }
    },

    # ── Firmware Vulnerabilities ──────────────────────────────────────────
    {
        "id": "IOT-FW-001",
        "name": "Outdated Firmware Version Detected",
        "severity": "high",
        "cvss": "7.5",
        "desc": "The device is running a firmware version that is significantly outdated. Older firmware versions may contain known vulnerabilities that have been patched in subsequent releases.",
        "fix": "Update device firmware through the manufacturer's mobile app or web interface. Enable automatic firmware updates where available.",
        "conditions": {
            "firmware_below": "2.0",
            "device_types": ["Smart Plug", "Smart Bulb", "Smart Hub"],
        }
    },

    # ── TLS/Encryption Vulnerabilities ───────────────────────────────────
    {
        "id": "CVE-2023-2617",
        "name": "Outdated TLS Version (TLS 1.0/1.1)",
        "severity": "medium",
        "cvss": "5.9",
        "desc": "The device accepts connections using deprecated TLS versions 1.0 or 1.1 which contain known cryptographic weaknesses including POODLE and BEAST vulnerabilities.",
        "fix": "Update device firmware to enforce TLS 1.2 or higher. Disable TLS 1.0 and 1.1 on all management interfaces.",
        "conditions": {
            "ports_open": [443, 8443],
        }
    },
    {
        "id": "CVE-2022-9911",
        "name": "Weak Cipher Suite (RC4) Detected",
        "severity": "medium",
        "cvss": "5.9",
        "desc": "The device supports the RC4 stream cipher which is cryptographically broken. RC4 is vulnerable to statistical bias attacks that can recover plaintext from encrypted communications.",
        "fix": "Update firmware to disable RC4 cipher suites and use AES-GCM or ChaCha20-Poly1305 instead.",
        "conditions": {
            "ports_open": [443, 8443],
        }
    },

    # ── Information Disclosure ────────────────────────────────────────────
    {
        "id": "INFO-001",
        "name": "Verbose Error Messages Exposing System Information",
        "severity": "low",
        "cvss": "3.7",
        "desc": "The device returns verbose error messages that disclose internal system information such as firmware version, software stack, or file paths. This information assists attackers in targeting device-specific exploits.",
        "fix": "Configure the device to return generic error messages. Disable debug mode in production.",
        "conditions": {
            "ports_open": [80, 8080],
        }
    },

    # ── Tuya / CozyLife Vulnerabilities ──────────────────────────────────
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

    # ── eWeLink / QIACHIP Vulnerabilities ────────────────────────────────
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
]
