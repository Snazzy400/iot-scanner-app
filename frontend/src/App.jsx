import { useState, useEffect, useRef } from "react";

const API = "https://reservation-suffering-dressing-jan.trycloudflare.com";

const SEVERITY_CONFIG = {
  critical: { color: "#FF3B3B", bg: "#FF3B3B18", label: "Critical", order: 0 },
  high:     { color: "#FF8C42", bg: "#FF8C4218", label: "High",     order: 1 },
  medium:   { color: "#FFD166", bg: "#FFD16618", label: "Medium",   order: 2 },
  low:      { color: "#06D6A0", bg: "#06D6A018", label: "Low",      order: 3 },
  safe:     { color: "#3B82F6", bg: "#3B82F618", label: "Safe",     order: 4 },
};

function getDeviceIcon(type = "") {
  const t = type.toLowerCase();
  if (t.includes("hub"))     return "⬡";
  if (t.includes("plug"))    return "⚡";
  if (t.includes("bulb"))    return "◎";
  if (t.includes("thermo"))  return "◈";
  if (t.includes("camera"))  return "⊙";
  if (t.includes("speaker")) return "◉";
  if (t.includes("sensor"))  return "◌";
  return "⬡";
}

function VulnBadge({ severity }) {
  const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.low;
  return (
    <span style={{ background: cfg.bg, border: `1px solid ${cfg.color}55`, borderRadius: 4, padding: "1px 7px", fontSize: 10, color: cfg.color, fontFamily: "monospace", fontWeight: 700, letterSpacing: 1, textTransform: "uppercase" }}>
      {cfg.label}
    </span>
  );
}

function ScanningOverlay({ stage, progress }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "70vh", gap: 32 }}>
      <div style={{ position: "relative", width: 120, height: 120 }}>
        <svg width="120" height="120" style={{ position: "absolute", animation: "spin 3s linear infinite" }}>
          <circle cx="60" cy="60" r="52" fill="none" stroke="#0ff3" strokeWidth="1" strokeDasharray="4 8"/>
        </svg>
        <svg width="120" height="120" style={{ position: "absolute", animation: "spinR 2s linear infinite" }}>
          <circle cx="60" cy="60" r="40" fill="none" stroke="#0ff5" strokeWidth="1" strokeDasharray="2 6"/>
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 36, color: "#00ffcc" }}>⊛</div>
      </div>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontFamily: "monospace", color: "#00ffcc", fontSize: 13, marginBottom: 16, minHeight: 20 }}>{stage}</div>
        <div style={{ width: 320, height: 4, background: "#ffffff0f", borderRadius: 2, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg,#00ffcc,#00aaff)", borderRadius: 2, transition: "width 0.3s" }} />
        </div>
        <div style={{ fontFamily: "monospace", color: "#ffffff40", fontSize: 12, marginTop: 8 }}>{Math.floor(progress)}%</div>
      </div>
    </div>
  );
}

function DeviceCard({ device, selected, onClick }) {
  const cfg = SEVERITY_CONFIG[device.status] || SEVERITY_CONFIG.safe;
  return (
    <div onClick={onClick} style={{ background: selected ? "#ffffff0d" : "#ffffff06", border: `1px solid ${selected ? cfg.color + "88" : "#ffffff12"}`, borderRadius: 12, padding: "14px 16px", cursor: "pointer", transition: "all 0.2s", position: "relative", overflow: "hidden" }}>
      {selected && <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: cfg.color, borderRadius: "3px 0 0 3px" }} />}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 20, color: cfg.color }}>{getDeviceIcon(device.type)}</span>
          <div>
            <div style={{ color: "#fff", fontSize: 13, fontWeight: 600, fontFamily: "monospace" }}>{device.type}</div>
            <div style={{ color: "#ffffff50", fontSize: 11, fontFamily: "monospace" }}>{device.ip}</div>
          </div>
        </div>
        <VulnBadge severity={device.status} />
      </div>
      <div style={{ display: "flex", gap: 10 }}>
        <span style={{ fontSize: 11, color: "#ffffff40", fontFamily: "monospace" }}>{device.vendor}</span>
        <span style={{ color: "#ffffff20" }}>·</span>
        <span style={{ fontSize: 11, color: "#ffffff40", fontFamily: "monospace" }}>{device.protocol}</span>
        {device.vulnerabilities?.length > 0 && <>
          <span style={{ color: "#ffffff20" }}>·</span>
          <span style={{ fontSize: 11, color: cfg.color, fontFamily: "monospace" }}>{device.vulnerabilities.length} vuln{device.vulnerabilities.length > 1 ? "s" : ""}</span>
        </>}
      </div>
    </div>
  );
}

function DeviceDetail({ device }) {
  const [open, setOpen] = useState(null);
  const cfg = SEVERITY_CONFIG[device.status] || SEVERITY_CONFIG.safe;

  return (
    <div style={{ height: "100%", overflowY: "auto" }}>
      <div style={{ background: "#ffffff06", border: "1px solid #ffffff12", borderRadius: 12, padding: 18, marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 48, height: 48, background: cfg.bg, border: `1px solid ${cfg.color}44`, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, color: cfg.color }}>
              {getDeviceIcon(device.type)}
            </div>
            <div>
              <div style={{ color: "#fff", fontSize: 15, fontWeight: 700, fontFamily: "monospace" }}>{device.type}</div>
              <div style={{ color: "#ffffff60", fontSize: 11, fontFamily: "monospace" }}>{device.vendor} · {device.mac}</div>
            </div>
          </div>
          <VulnBadge severity={device.status} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {[
            ["IP Address", device.ip],
            ["Protocol",   device.protocol],
            ["Firmware",   device.firmware],
            ["Open Ports", device.ports?.map(p => p.port).join(", ") || "none"],
          ].map(([k, v]) => (
            <div key={k} style={{ background: "#ffffff05", borderRadius: 8, padding: "8px 12px" }}>
              <div style={{ color: "#ffffff40", fontSize: 10, fontFamily: "monospace", letterSpacing: 1, marginBottom: 2, textTransform: "uppercase" }}>{k}</div>
              <div style={{ color: "#ffffffcc", fontSize: 12, fontFamily: "monospace" }}>{v}</div>
            </div>
          ))}
        </div>
        {device.ports?.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <div style={{ color: "#ffffff30", fontSize: 10, fontFamily: "monospace", letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>Services Detected</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
              {device.ports.map(p => (
                <span key={p.port} style={{ background: "#ffffff08", border: "1px solid #ffffff15", borderRadius: 4, padding: "2px 8px", fontSize: 10, color: "#ffffff70", fontFamily: "monospace" }}>
                  {p.port}/{p.service}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div style={{ color: "#ffffff50", fontSize: 11, fontFamily: "monospace", letterSpacing: 2, textTransform: "uppercase", marginBottom: 8 }}>
        Vulnerabilities ({device.vulnerabilities?.length || 0})
      </div>
      {!device.vulnerabilities?.length ? (
        <div style={{ background: "#06D6A010", border: "1px solid #06D6A030", borderRadius: 12, padding: 20, textAlign: "center" }}>
          <div style={{ fontSize: 22, marginBottom: 6 }}>✓</div>
          <div style={{ color: "#06D6A0", fontFamily: "monospace", fontSize: 13 }}>No vulnerabilities detected</div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {device.vulnerabilities.map((v, i) => {
            const isOpen = open === i;
            const vc = SEVERITY_CONFIG[v.severity] || SEVERITY_CONFIG.low;
            return (
              <div key={v.id} onClick={() => setOpen(isOpen ? null : i)} style={{ background: "#ffffff06", border: `1px solid ${isOpen ? vc.color + "44" : "#ffffff10"}`, borderRadius: 10, padding: 14, cursor: "pointer", transition: "all 0.2s" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: isOpen ? 12 : 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <VulnBadge severity={v.severity} />
                    <span style={{ color: "#ffffffcc", fontSize: 13, fontFamily: "monospace" }}>{v.name}</span>
                  </div>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ color: "#ffffff30", fontSize: 10, fontFamily: "monospace" }}>{v.id}</span>
                    <span style={{ color: "#ffffff40" }}>{isOpen ? "▴" : "▾"}</span>
                  </div>
                </div>
                {isOpen && (
                  <div style={{ borderTop: "1px solid #ffffff0a", paddingTop: 12 }}>
                    {v.cvss && v.cvss !== "N/A" && (
                      <div style={{ marginBottom: 8 }}>
                        <span style={{ background: "#ffffff08", border: "1px solid #ffffff15", borderRadius: 4, padding: "2px 8px", fontSize: 10, color: "#ffffff60", fontFamily: "monospace" }}>CVSS {v.cvss}</span>
                      </div>
                    )}
                    <div style={{ color: "#ffffff70", fontSize: 12, fontFamily: "monospace", lineHeight: 1.7, marginBottom: 12 }}>{v.desc}</div>
                    <div style={{ background: "#06D6A010", border: "1px solid #06D6A030", borderRadius: 8, padding: 12 }}>
                      <div style={{ color: "#06D6A0", fontSize: 10, fontFamily: "monospace", letterSpacing: 1, textTransform: "uppercase", marginBottom: 4 }}>↳ Remediation</div>
                      <div style={{ color: "#06D6A0cc", fontSize: 12, fontFamily: "monospace", lineHeight: 1.6 }}>{v.fix}</div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function RiskReport({ results }) {
  const { devices = [], severity_counts = {}, security_score = 0, total_vulnerabilities = 0 } = results;
  const counts = { critical: 0, high: 0, medium: 0, low: 0, ...severity_counts };
  const scoreColor = security_score >= 80 ? "#06D6A0" : security_score >= 50 ? "#FFD166" : "#FF3B3B";
  const allVulns = devices.flatMap(d => (d.vulnerabilities || []).map(v => ({ ...v, device: d.type, ip: d.ip })));

  return (
    <div style={{ height: "100%", overflowY: "auto" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
        <div style={{ background: "#ffffff06", border: "1px solid #ffffff10", borderRadius: 12, padding: 20, gridColumn: "1 / -1", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ color: "#ffffff50", fontSize: 11, fontFamily: "monospace", letterSpacing: 2, textTransform: "uppercase", marginBottom: 6 }}>Network Security Score</div>
            <div style={{ color: "#ffffff80", fontSize: 13, fontFamily: "monospace" }}>{total_vulnerabilities} vulnerabilities · {devices.length} devices scanned</div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 52, fontWeight: 800, color: scoreColor, fontFamily: "monospace", lineHeight: 1 }}>{security_score}</div>
            <div style={{ color: scoreColor + "88", fontSize: 11, fontFamily: "monospace" }}>/ 100</div>
          </div>
        </div>
        {Object.entries(counts).map(([sev, count]) => {
          const cfg = SEVERITY_CONFIG[sev];
          return (
            <div key={sev} style={{ background: cfg.bg, border: `1px solid ${cfg.color}30`, borderRadius: 10, padding: "14px 18px" }}>
              <div style={{ color: cfg.color, fontSize: 10, fontFamily: "monospace", letterSpacing: 2, textTransform: "uppercase", marginBottom: 4 }}>{cfg.label}</div>
              <div style={{ color: cfg.color, fontSize: 32, fontWeight: 800, fontFamily: "monospace" }}>{count}</div>
            </div>
          );
        })}
      </div>
      {allVulns.length > 0 && <>
        <div style={{ color: "#ffffff50", fontSize: 11, fontFamily: "monospace", letterSpacing: 2, textTransform: "uppercase", marginBottom: 10 }}>All Findings</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {allVulns.sort((a, b) => (SEVERITY_CONFIG[a.severity]?.order ?? 9) - (SEVERITY_CONFIG[b.severity]?.order ?? 9)).map((v, i) => (
            <div key={i} style={{ background: "#ffffff06", border: "1px solid #ffffff0d", borderRadius: 8, padding: "10px 14px", display: "flex", alignItems: "center", gap: 12 }}>
              <VulnBadge severity={v.severity} />
              <div style={{ flex: 1 }}>
                <span style={{ color: "#ffffffcc", fontSize: 12, fontFamily: "monospace" }}>{v.name}</span>
                <span style={{ color: "#ffffff30", fontSize: 11, fontFamily: "monospace" }}> — {v.device}</span>
              </div>
              <span style={{ color: "#ffffff30", fontSize: 10, fontFamily: "monospace" }}>{v.ip}</span>
            </div>
          ))}
        </div>
      </>}
    </div>
  );
}

function HistoryTab({ onLoad, refreshKey }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(`${API}/api/scans`)
      .then(r => r.json())
      .then(data => { setHistory(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [refreshKey]);

  const handleDelete = async (scan_id) => {
    setDeleting(scan_id);
    try {
      await fetch(`${API}/api/scans/${scan_id}`, { method: "DELETE" });
      setHistory(prev => prev.filter(s => s.scan_id !== scan_id));
    } catch (e) {
      alert("Failed to delete scan.");
    }
    setDeleting(null);
    setConfirmDelete(null);
  };

  const handleDeleteAll = async () => {
    setDeleting("all");
    try {
      await fetch(`${API}/api/scans`, { method: "DELETE" });
      setHistory([]);
    } catch (e) {
      alert("Failed to delete all scans.");
    }
    setDeleting(null);
    setConfirmDelete(null);
  };

  if (loading) return <div style={{ color: "#ffffff40", fontFamily: "monospace", textAlign: "center", paddingTop: 60 }}>Loading scan history...</div>;
  if (!history.length) return <div style={{ color: "#ffffff30", fontFamily: "monospace", textAlign: "center", paddingTop: 60 }}>No previous scans found.</div>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
        {confirmDelete === "all" ? (
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ color: "#ffffff50", fontSize: 11, fontFamily: "monospace" }}>Delete all scans?</span>
            <button onClick={handleDeleteAll} style={{ background: "#FF3B3B22", border: "1px solid #FF3B3B44", color: "#FF3B3B", borderRadius: 6, padding: "4px 12px", fontSize: 11, cursor: "pointer", fontFamily: "monospace" }}>
              {deleting === "all" ? "Deleting..." : "Confirm"}
            </button>
            <button onClick={() => setConfirmDelete(null)} style={{ background: "#ffffff08", border: "1px solid #ffffff15", color: "#ffffff60", borderRadius: 6, padding: "4px 12px", fontSize: 11, cursor: "pointer", fontFamily: "monospace" }}>
              Cancel
            </button>
          </div>
        ) : (
          <button onClick={() => setConfirmDelete("all")} style={{ background: "#FF3B3B12", border: "1px solid #FF3B3B33", color: "#FF3B3B88", borderRadius: 6, padding: "5px 14px", fontSize: 11, cursor: "pointer", fontFamily: "monospace", letterSpacing: 1 }}>
            ✕ Clear All History
          </button>
        )}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {history.map(s => {
          const scoreColor = s.score >= 80 ? "#06D6A0" : s.score >= 50 ? "#FFD166" : "#FF3B3B";
          const isConfirming = confirmDelete === s.scan_id;
          return (
            <div key={s.scan_id} style={{ background: "#ffffff06", border: "1px solid #ffffff10", borderRadius: 10, padding: "14px 18px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div onClick={() => onLoad(s.scan_id)} style={{ flex: 1, cursor: "pointer" }}>
                <div style={{ color: "#ffffffcc", fontSize: 13, fontFamily: "monospace", marginBottom: 4 }}>{s.target}</div>
                <div style={{ color: "#ffffff40", fontSize: 11, fontFamily: "monospace" }}>{new Date(s.scanned_at).toLocaleString()} · {s.device_count} devices · {s.vuln_count} vulns</div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 24, fontWeight: 800, color: scoreColor, fontFamily: "monospace" }}>{s.score}</div>
                  <div style={{ color: "#ffffff30", fontSize: 10, fontFamily: "monospace" }}>score</div>
                </div>
                {isConfirming ? (
                  <div style={{ display: "flex", gap: 6 }}>
                    <button onClick={() => handleDelete(s.scan_id)} style={{ background: "#FF3B3B22", border: "1px solid #FF3B3B44", color: "#FF3B3B", borderRadius: 6, padding: "4px 10px", fontSize: 10, cursor: "pointer", fontFamily: "monospace" }}>
                      {deleting === s.scan_id ? "..." : "Delete"}
                    </button>
                    <button onClick={() => setConfirmDelete(null)} style={{ background: "#ffffff08", border: "1px solid #ffffff15", color: "#ffffff50", borderRadius: 6, padding: "4px 10px", fontSize: 10, cursor: "pointer", fontFamily: "monospace" }}>
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button onClick={(e) => { e.stopPropagation(); setConfirmDelete(s.scan_id); }} style={{ background: "transparent", border: "1px solid #ffffff15", color: "#ffffff30", borderRadius: 6, padding: "4px 10px", fontSize: 11, cursor: "pointer", fontFamily: "monospace" }}>
                    ✕
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function App() {
  const [phase, setPhase]               = useState("idle");
  const [scanStage, setScanStage]       = useState("");
  const [scanProgress, setScanProgress] = useState(0);
  const [results, setResults]           = useState(null);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [activeTab, setActiveTab]       = useState("devices");
  const [apiOnline, setApiOnline]       = useState(null);
  const [historyKey, setHistoryKey]     = useState(0);
  const pollRef = useRef(null);

  useEffect(() => {
    fetch(`${API}/`)
      .then(r => r.json())
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  const goHome = () => {
    if (pollRef.current) clearInterval(pollRef.current);
    setPhase("idle");
    setResults(null);
    setSelectedDevice(null);
    setHistoryKey(k => k + 1);
  };

  const startScan = async () => {
    setPhase("scanning");
    setScanProgress(0);
    setScanStage("Initializing...");
    setResults(null);
    setSelectedDevice(null);
    try {
      const res = await fetch(`${API}/api/scan/start`, { method: "POST" });
      const { scan_id } = await res.json();
      pollRef.current = setInterval(async () => {
        const s = await fetch(`${API}/api/scan/status/${scan_id}`).then(r => r.json());
        setScanStage(s.stage || "");
        setScanProgress(s.progress || 0);
        if (s.status === "complete") {
          clearInterval(pollRef.current);
          setResults(s.results);
          setSelectedDevice(s.results.devices?.[0] || null);
          setPhase("results");
          setActiveTab("devices");
          setHistoryKey(k => k + 1);
        } else if (s.status === "error") {
          clearInterval(pollRef.current);
          setPhase("idle");
          alert("Scan failed: " + s.error);
        }
      }, 400);
    } catch (e) {
      setPhase("idle");
      alert("Cannot reach backend. Is the API running on port 8000?");
    }
  };

  const loadHistoryScan = async (scan_id) => {
    const data = await fetch(`${API}/api/scans/${scan_id}`).then(r => r.json());
    setResults(data);
    setSelectedDevice(data.devices?.[0] || null);
    setPhase("results");
    setActiveTab("devices");
  };

  const criticalCount = results?.severity_counts?.critical || 0;
  const highCount     = results?.severity_counts?.high     || 0;

  return (
    <div style={{ minHeight: "100vh", width: "100%", background: "#080c12", color: "#fff", fontFamily: "monospace", position: "relative" }}>
      <style>{`
        @keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
        @keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
        @keyframes spinR{from{transform:rotate(360deg)}to{transform:rotate(0)}}
        ::-webkit-scrollbar{width:4px} ::-webkit-scrollbar-thumb{background:#ffffff20;border-radius:2px}
        *{box-sizing:border-box} html,body{margin:0;padding:0;width:100%;overflow-x:hidden}
      `}</style>

      <div style={{ position: "fixed", inset: 0, backgroundImage: "linear-gradient(#00ffcc04 1px,transparent 1px),linear-gradient(90deg,#00ffcc04 1px,transparent 1px)", backgroundSize: "40px 40px", pointerEvents: "none", zIndex: 0 }} />
      <div style={{ position: "fixed", inset: 0, background: "radial-gradient(ellipse at 20% 20%,#00ffcc08,transparent 60%),radial-gradient(ellipse at 80% 80%,#0044ff06,transparent 60%)", pointerEvents: "none", zIndex: 0 }} />

      <div style={{ position: "relative", zIndex: 1, padding: "24px 32px" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            {phase !== "idle" && (
              <button onClick={goHome} style={{ background: "#ffffff08", border: "1px solid #ffffff18", color: "#ffffff70", borderRadius: 8, padding: "7px 16px", fontSize: 12, cursor: "pointer", fontFamily: "monospace", letterSpacing: 1, transition: "all 0.2s" }}>
                ← Home
              </button>
            )}
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 2 }}>
                <span style={{ fontSize: 20, color: "#00ffcc" }}>⊛</span>
                <span style={{ fontSize: 18, fontWeight: 800, letterSpacing: 3, color: "#fff", textTransform: "uppercase" }}>IoT Scanner</span>
                <span style={{ background: "#00ffcc15", border: "1px solid #00ffcc30", borderRadius: 4, padding: "1px 8px", fontSize: 9, color: "#00ffcc", letterSpacing: 2 }}>v1.0</span>
                {apiOnline !== null && (
                  <span style={{ background: apiOnline ? "#06D6A015" : "#FF3B3B15", border: `1px solid ${apiOnline ? "#06D6A040" : "#FF3B3B40"}`, borderRadius: 4, padding: "1px 8px", fontSize: 9, color: apiOnline ? "#06D6A0" : "#FF3B3B", letterSpacing: 2 }}>
                    API {apiOnline ? "ONLINE" : "OFFLINE"}
                  </span>
                )}
              </div>
              <div style={{ color: "#ffffff30", fontSize: 11, letterSpacing: 1 }}>Smart Home Vulnerability Assessment · 192.168.100.0/24</div>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {phase === "results" && criticalCount + highCount > 0 && (
              <div style={{ display: "flex", gap: 8, marginRight: 8 }}>
                {[["critical", criticalCount + " Critical"], ["high", highCount + " High"]].filter(([, c]) => parseInt(c) > 0).map(([sev, label]) => (
                  <div key={sev} style={{ background: SEVERITY_CONFIG[sev].bg, border: `1px solid ${SEVERITY_CONFIG[sev].color}44`, borderRadius: 6, padding: "4px 12px", fontSize: 11, color: SEVERITY_CONFIG[sev].color }}>
                    {label}
                  </div>
                ))}
              </div>
            )}
            <button onClick={startScan} disabled={phase === "scanning"} style={{ background: phase === "idle" ? "#00ffcc" : "#00ffcc22", border: `1px solid ${phase === "idle" ? "#00ffcc" : "#00ffcc44"}`, color: phase === "idle" ? "#080c12" : "#00ffcc", borderRadius: 8, padding: "9px 20px", fontSize: 12, fontWeight: 800, cursor: phase === "scanning" ? "not-allowed" : "pointer", fontFamily: "monospace", letterSpacing: 2, textTransform: "uppercase", transition: "all 0.2s", opacity: phase === "scanning" ? 0.7 : 1 }}>
              {phase === "idle" ? "▶ Run Scan" : phase === "scanning" ? "Scanning..." : "↺ Rescan"}
            </button>
          </div>
        </div>

        {/* IDLE */}
        {phase === "idle" && (
          <div style={{ animation: "fadeIn 0.4s ease" }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 260, gap: 20, marginBottom: 32 }}>
              <div style={{ width: 90, height: 90, border: "1px solid #00ffcc22", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, color: "#00ffcc33" }}>⊛</div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: "#ffffff50", marginBottom: 6, letterSpacing: 2 }}>NETWORK IDLE</div>
                <div style={{ color: "#ffffff30", fontSize: 12, letterSpacing: 1 }}>Press Run Scan to discover and assess IoT devices.</div>
              </div>
            </div>
            <div style={{ color: "#ffffff50", fontSize: 11, letterSpacing: 2, textTransform: "uppercase", marginBottom: 12 }}>Previous Scans</div>
            <HistoryTab onLoad={loadHistoryScan} refreshKey={historyKey} />
          </div>
        )}

        {/* SCANNING */}
        {phase === "scanning" && <ScanningOverlay stage={scanStage} progress={scanProgress} />}

        {/* RESULTS */}
        {phase === "results" && results && (
          <div style={{ animation: "fadeIn 0.4s ease" }}>
            <div style={{ display: "flex", gap: 4, marginBottom: 18 }}>
              {[["devices", `⊞  Devices (${results.devices_found})`], ["report", "≡  Risk Report"], ["history", "⊕  History"]].map(([tab, label]) => (
                <button key={tab} onClick={() => setActiveTab(tab)} style={{ background: activeTab === tab ? "#ffffff0f" : "transparent", border: `1px solid ${activeTab === tab ? "#ffffff22" : "transparent"}`, borderBottom: activeTab === tab ? "1px solid #00ffcc66" : "1px solid transparent", color: activeTab === tab ? "#fff" : "#ffffff40", borderRadius: "8px 8px 0 0", padding: "8px 18px", fontSize: 12, cursor: "pointer", fontFamily: "monospace", letterSpacing: 1, transition: "all 0.2s" }}>
                  {label}
                </button>
              ))}
              <div style={{ flex: 1, borderBottom: "1px solid #ffffff10" }} />
              <div style={{ display: "flex", alignItems: "center", paddingRight: 4, borderBottom: "1px solid #ffffff10" }}>
                <span style={{ color: "#ffffff30", fontSize: 11, fontFamily: "monospace" }}>
                  {results.total_vulnerabilities} vulns · {results.devices_found} devices · {new Date(results.scan_time).toLocaleTimeString()}
                </span>
              </div>
            </div>

            {activeTab === "devices" && (
              <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 16, height: "calc(100vh - 200px)" }}>
                <div style={{ display: "flex", flexDirection: "column", gap: 8, overflowY: "auto" }}>
                  {results.devices.map((d, i) => (
                    <DeviceCard key={i} device={d} selected={selectedDevice?.ip === d.ip} onClick={() => setSelectedDevice(d)} />
                  ))}
                </div>
                <div style={{ background: "#ffffff04", border: "1px solid #ffffff0d", borderRadius: 14, padding: 20, overflowY: "auto" }}>
                  {selectedDevice ? <DeviceDetail device={selectedDevice} /> : (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "#ffffff20", fontSize: 13 }}>← Select a device</div>
                  )}
                </div>
              </div>
            )}

            {activeTab === "report" && (
              <div style={{ background: "#ffffff04", border: "1px solid #ffffff0d", borderRadius: 14, padding: 20, height: "calc(100vh - 200px)", overflowY: "auto" }}>
                <RiskReport results={results} />
              </div>
            )}

            {activeTab === "history" && (
              <div style={{ background: "#ffffff04", border: "1px solid #ffffff0d", borderRadius: 14, padding: 20, height: "calc(100vh - 200px)", overflowY: "auto" }}>
                <HistoryTab onLoad={loadHistoryScan} refreshKey={historyKey} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
