"""
port_scanner.py  –  TCP port scanning for IoT-relevant ports
Uses nmap if available, falls back to asyncio socket probing.
"""

import asyncio
import socket

# Ports commonly found on IoT / smart home devices
IOT_PORTS = [21, 22, 23, 80, 443, 554, 1883, 4070, 5683, 7547, 8080, 8443, 8883, 9999, 49152]

PORT_SERVICES = {
    21:    "FTP",
    22:    "SSH",
    23:    "Telnet",
    80:    "HTTP",
    443:   "HTTPS",
    554:   "RTSP (Camera stream)",
    1883:  "MQTT (unencrypted)",
    4070:  "Amazon Music / Alexa",
    5683:  "CoAP",
    7547:  "TR-069 (ISP management)",
    8080:  "HTTP-alt",
    8443:  "HTTPS-alt",
    8883:  "MQTT (TLS)",
    9999:  "TP-Link Kasa",
    49152: "UPnP",
}


async def scan_ports(ip: str, timeout: float = 1.0) -> list[dict]:
    """
    Scan IoT-relevant ports on the given IP.
    Returns list of {port, service, open} dicts for open ports only.
    """
    try:
        import nmap
        return _nmap_scan(ip)
    except ImportError:
        pass
    except Exception as e:
        print(f"⚠️  nmap port scan failed for {ip}: {e}")

    # Fallback: asyncio socket probing
    return await _async_socket_scan(ip, timeout)


def _nmap_scan(ip: str) -> list[dict]:
    import nmap
    nm = nmap.PortScanner()
    port_list = ",".join(str(p) for p in IOT_PORTS)
    nm.scan(ip, port_list, arguments="-T4 --host-timeout 15s")
    results = []
    if ip in nm.all_hosts():
        for proto in nm[ip].all_protocols():
            for port, data in nm[ip][proto].items():
                if data["state"] == "open":
                    results.append({
                        "port": port,
                        "service": data.get("name") or PORT_SERVICES.get(port, "unknown"),
                        "open": True,
                    })
    return results


async def _async_socket_scan(ip: str, timeout: float) -> list[dict]:
    """Lightweight asyncio-based TCP connect scan."""
    results = []
    tasks = [_probe_port(ip, port, timeout) for port in IOT_PORTS]
    outcomes = await asyncio.gather(*tasks, return_exceptions=True)
    for port, outcome in zip(IOT_PORTS, outcomes):
        if outcome is True:
            results.append({
                "port": port,
                "service": PORT_SERVICES.get(port, "unknown"),
                "open": True,
            })
    return results


async def _probe_port(ip: str, port: int, timeout: float) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False
