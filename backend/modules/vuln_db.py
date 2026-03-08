"""
vuln_db.py  –  IoT Smart Home Vulnerability Knowledge Base
Each entry maps device characteristics → known CVE / security issue.
Sources: NVD, Mitre, Palo Alto Unit 42, OWASP IoT Top 10
"""

VULNERABILITY_DB = [

    # ── Default / Weak Credentials ────────────────────────────────────────────
    {
        "id": "IOT-CRED-001",
        "name": "Default Credentials Not Changed",
        "severity": "critical",
        "cvss": "9.8",
        "desc": (
            "Device is likely still using factory-default credentials (e.g. admin/admin). "
            "Default credentials are publicly documented and are the primary method used "
            "by botnets like Mirai to gain initial access."
        ),
        "fix": "Log into the device admin panel and set a unique, strong password immediately.",
        "match": {
            "device_types": ["hub", "plug", "camera", "router", "switch"],
        },
    },
    {
        "id": "CVE-2016-10372",
        "name": "Mirai Botnet Default Credential Vector",
        "severity": "critical",
        "cvss": "9.8",
        "desc": (
            "Telnet service is exposed (port 23). Mirai and successor botnets actively "
            "scan for Telnet with default credentials to recruit devices into DDoS botnets."
        ),
        "fix": "Disable Telnet immediately. Use SSH (port 22) with key-based auth if remote access is needed.",
        "match": {
            "ports_open": [23],
        },
    },

    # ── Unencrypted Communications ────────────────────────────────────────────
    {
        "id": "IOT-NET-001",
        "name": "Unencrypted HTTP Management Interface",
        "severity": "high",
        "cvss": "7.5",
        "desc": (
            "Web management interface is running on plain HTTP (port 80) without TLS encryption. "
            "Credentials and commands transmitted in cleartext can be intercepted by anyone "
            "on the local network (man-in-the-middle attack)."
        ),
        "fix": "Enable HTTPS in device settings. If unavailable, disable the web interface and manage via the mobile app over a secure connection.",
        "match": {
            "ports_open": [80],
            "ports_absent": [443],
        },
    },
    {
        "id": "IOT-NET-002",
        "name": "Unencrypted MQTT Broker (Port 1883)",
        "severity": "high",
        "cvss": "7.4",
        "desc": (
            "Device communicates over unencrypted MQTT on port 1883. All IoT messages "
            "(device state, commands, sensor data) are transmitted in plaintext. "
            "Estimated 98%% of IoT traffic is unencrypted (Palo Alto Networks, 2025)."
        ),
        "fix": "Migrate to MQTT over TLS on port 8883. Update broker and client configurations.",
        "match": {
            "ports_open": [1883],
        },
    },
    {
        "id": "IOT-NET-003",
        "name": "FTP Service Exposed",
        "severity": "high",
        "cvss": "7.5",
        "desc": (
            "FTP service is running on port 21. FTP transmits credentials and data "
            "in plaintext and has numerous known vulnerabilities."
        ),
        "fix": "Disable FTP service. Use SFTP or SCP if file transfer is required.",
        "match": {
            "ports_open": [21],
        },
    },

    # ── TP-Link / Smart Plug specific ─────────────────────────────────────────
    {
        "id": "CVE-2021-4045",
        "name": "TP-Link Tapo Command Injection via UPnP",
        "severity": "high",
        "cvss": "9.8",
        "desc": (
            "Unauthenticated remote code execution vulnerability in TP-Link smart plugs "
            "via the UPnP service on port 9999. An attacker on the local network can "
            "inject arbitrary commands without authentication."
        ),
        "fix": "Update firmware to v1.0.14 or later via the Tapo app. Disable UPnP if not required.",
        "match": {
            "vendors": ["tp-link"],
            "ports_open": [9999],
        },
    },
    {
        "id": "CVE-2023-5614",
        "name": "TP-Link Wi-Fi PSK Stored in Cleartext",
        "severity": "medium",
        "cvss": "5.5",
        "desc": (
            "TP-Link smart plug firmware stores the Wi-Fi pre-shared key (PSK) in "
            "plaintext in device memory. An attacker with physical or network access "
            "can extract the home Wi-Fi password."
        ),
        "fix": "Update firmware. Rotate Wi-Fi credentials after patching as a precaution.",
        "match": {
            "vendors": ["tp-link"],
        },
    },

    # ── ZigBee Protocol ───────────────────────────────────────────────────────
    {
        "id": "CVE-2020-6007",
        "name": "ZigBee Replay Attack — Insufficient Nonce Protection",
        "severity": "medium",
        "cvss": "6.5",
        "desc": (
            "ZigBee protocol implementations in smart bulbs and sensors lack proper "
            "nonce/timestamp validation, enabling replay attacks. A captured command "
            "(e.g. 'turn on lights') can be re-broadcast to reproduce the action illicitly."
        ),
        "fix": "Ensure Philips Hue Bridge firmware is up to date. Segment ZigBee devices on a separate VLAN.",
        "match": {
            "protocols": ["zigbee"],
        },
    },
    {
        "id": "IOT-PROTO-002",
        "name": "ZigBee Key Interception Risk",
        "severity": "medium",
        "cvss": "5.9",
        "desc": (
            "ZigBee devices exchange network keys during the join procedure. "
            "Weak key exchange mechanisms allow passive eavesdroppers to capture "
            "the network key and decrypt subsequent traffic."
        ),
        "fix": "Use Zigbee 3.0 certified devices. Enable install code-based joining in your ZigBee coordinator.",
        "match": {
            "protocols": ["zigbee"],
        },
    },

    # ── TLS / Cryptographic weaknesses ───────────────────────────────────────
    {
        "id": "CVE-2023-2617",
        "name": "Outdated TLS Version (TLS 1.0 / 1.1)",
        "severity": "medium",
        "cvss": "5.9",
        "desc": (
            "Device negotiates TLS 1.0 or TLS 1.1, both deprecated by RFC 8996. "
            "These versions are vulnerable to POODLE and BEAST attacks which can "
            "allow decryption of sensitive communications."
        ),
        "fix": "Update device firmware to enforce TLS 1.2 minimum. Contact vendor if no update is available.",
        "match": {
            "device_types": ["speaker", "thermostat"],
            "vendors": ["amazon", "google", "nest"],
        },
    },
    {
        "id": "CVE-2022-9911",
        "name": "Weak Cipher Suite — RC4 Accepted",
        "severity": "medium",
        "cvss": "5.9",
        "desc": (
            "Device accepts RC4 cipher suites which are cryptographically broken "
            "and prohibited by RFC 7465. Traffic encrypted with RC4 can be decrypted "
            "by a sufficiently resourced attacker."
        ),
        "fix": "Firmware update required to enforce modern cipher suites (AES-GCM). Restrict network access until patched.",
        "match": {
            "device_types": ["speaker"],
            "vendors": ["amazon"],
        },
    },

    # ── TR-069 / ISP management port ─────────────────────────────────────────
    {
        "id": "IOT-NET-004",
        "name": "TR-069 Management Port Exposed (7547)",
        "severity": "high",
        "cvss": "8.1",
        "desc": (
            "Port 7547 (CWMP/TR-069) is open and potentially exposed. This port is used "
            "by ISPs for remote management. Known exploits (e.g. Mirai variant attacks in 2016) "
            "have targeted this port to compromise home routers and IoT gateways."
        ),
        "fix": "Block port 7547 at your firewall/router. Disable TR-069 in router settings if ISP support is not needed.",
        "match": {
            "ports_open": [7547],
        },
    },

    # ── UPnP ─────────────────────────────────────────────────────────────────
    {
        "id": "IOT-NET-005",
        "name": "UPnP Service Exposed (Port 49152)",
        "severity": "medium",
        "cvss": "6.5",
        "desc": (
            "Universal Plug and Play (UPnP) is active. UPnP has no authentication "
            "mechanism and historically has been exploited to expose internal services "
            "to the internet and pivot through home networks."
        ),
        "fix": "Disable UPnP on the device and on your router unless specifically required.",
        "match": {
            "ports_open": [49152],
        },
    },

    # ── Firmware ──────────────────────────────────────────────────────────────
    {
        "id": "IOT-FW-001",
        "name": "Outdated Firmware — Known CVEs May Apply",
        "severity": "medium",
        "cvss": "6.0",
        "desc": (
            "Device is running an outdated firmware version. Outdated firmware may contain "
            "unpatched vulnerabilities. Many IoT devices are never updated after initial setup, "
            "leaving them permanently exposed (Bakhshi et al., 2024)."
        ),
        "fix": "Check the manufacturer's website or app for a firmware update. Enable auto-update if available.",
        "match": {
            "firmware_below": "2.0.0",
            "device_types": ["plug", "bulb", "sensor"],
        },
    },

    # ── RTSP Camera Stream ────────────────────────────────────────────────────
    {
        "id": "IOT-CAM-001",
        "name": "RTSP Camera Stream Potentially Unauthenticated",
        "severity": "high",
        "cvss": "8.6",
        "desc": (
            "RTSP video stream port 554 is open. Many IP cameras expose RTSP streams "
            "without authentication, allowing anyone on the network (or internet if port "
            "forwarded) to view live video footage."
        ),
        "fix": "Enable RTSP authentication in camera settings. Ensure port 554 is not forwarded through your router.",
        "match": {
            "ports_open": [554],
        },
    },

    # ── Informational ─────────────────────────────────────────────────────────
    {
        "id": "INFO-001",
        "name": "Verbose Error Messages Expose System Info",
        "severity": "low",
        "cvss": "3.1",
        "desc": (
            "API or web interface returns verbose error messages containing software "
            "version numbers, stack traces, or internal paths. This information assists "
            "attackers in identifying specific exploits to use."
        ),
        "fix": "No immediate user action required. Monitor vendor for firmware updates that address information disclosure.",
        "match": {
            "device_types": ["thermostat", "hub"],
            "vendors": ["nest", "raspberry"],
        },
    },
]
