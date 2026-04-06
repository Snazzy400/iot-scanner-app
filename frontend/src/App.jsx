import { useState, useEffect, useRef } from "react";

const API = " https://lbs-invention-correspondence-brilliant.trycloudflare.com ";

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

// ── Login Page ────────────────────────────────────────────────────────────────
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  const handleLogin = async () => {
    if (!username || !password) { setError("Please enter username and password."); return; }
    setLoading(true); setError("");
    try {
      const res = await fetch(`${API}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem("iot_token", data.access_token);
        localStorage.setItem("iot_username", data.username);
        onLogin(data.access_token, data.username);
      } else {
        const err = await res.json();
        setError(err.detail || "Login failed.");
      }
    } catch {
      setError("Cannot reach backend. Make sure the API is running.");
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", width: "100vw", background: "#080c12", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", position: "relative", overflow: "hidden" }}>
      <style>{`
        @keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
        @keyframes fadeIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
        *{box-sizing:border-box} html,body{margin:0;padding:0}
        input::placeholder{color:#ffffff30}
      `}</style>

      {/* BG */}
      <div style={{ position: "fixed", inset: 0, backgroundImage: "linear-gradient(#00ffcc04 1px,transparent 1px),linear-gradient(90deg,#00ffcc04 1px,transparent 1px)", backgroundSize: "40px 40px", pointerEvents: "none" }} />
      <div style={{ position: "fixed", inset: 0, background: "radial-gradient(ellipse at 50% 40%,#00ffcc0a,transparent 60%)", pointerEvents: "none" }} />

      <div style={{ position: "relative", zIndex: 1, width: 380, animation: "fadeIn 0.4s ease" }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 36 }}>
          <img src="data:image/webp;base64,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" alt="NEU Logo" style={{ width: 110, height: 110, objectFit: "contain", marginBottom: 12, filter: "drop-shadow(0 0 12px #00ffcc22)" }} />
          <div style={{ fontSize: 20, fontWeight: 800, letterSpacing: 4, color: "#fff", textTransform: "uppercase" }}>IoT Scanner</div>
          <div style={{ color: "#00ffcc", fontSize: 10, letterSpacing: 2, marginTop: 2 }}>NORTH-EASTERN UNIVERSITY GOMBE</div>
          <div style={{ color: "#ffffff30", fontSize: 10, letterSpacing: 2, marginTop: 2 }}>SMART HOME VULNERABILITY ASSESSMENT</div>
        </div>

        {/* Card */}
        <div style={{ background: "#0f1520", border: "1px solid #ffffff12", borderRadius: 16, padding: 32 }}>
          <div style={{ color: "#ffffff60", fontSize: 11, letterSpacing: 2, textTransform: "uppercase", marginBottom: 20 }}>Admin Login</div>

          {/* Username */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ color: "#ffffff40", fontSize: 10, letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>Username</div>
            <input
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
              placeholder="Enter username"
              style={{ width: "100%", background: "#ffffff08", border: "1px solid #ffffff15", borderRadius: 8, padding: "10px 14px", color: "#fff", fontFamily: "monospace", fontSize: 13, outline: "none", transition: "border 0.2s" }}
            />
          </div>

          {/* Password */}
          <div style={{ marginBottom: 24 }}>
            <div style={{ color: "#ffffff40", fontSize: 10, letterSpacing: 1, textTransform: "uppercase", marginBottom: 6 }}>Password</div>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleLogin()}
              placeholder="Enter password"
              style={{ width: "100%", background: "#ffffff08", border: "1px solid #ffffff15", borderRadius: 8, padding: "10px 14px", color: "#fff", fontFamily: "monospace", fontSize: 13, outline: "none", transition: "border 0.2s" }}
            />
          </div>

          {/* Error */}
          {error && (
            <div style={{ background: "#FF3B3B12", border: "1px solid #FF3B3B33", borderRadius: 8, padding: "10px 14px", color: "#FF3B3B", fontSize: 12, marginBottom: 16 }}>
              {error}
            </div>
          )}

          {/* Login button */}
          <button
            onClick={handleLogin}
            disabled={loading}
            style={{ width: "100%", background: loading ? "#00ffcc44" : "#00ffcc", border: "none", borderRadius: 8, padding: "12px", color: "#080c12", fontFamily: "monospace", fontSize: 13, fontWeight: 800, letterSpacing: 2, textTransform: "uppercase", cursor: loading ? "not-allowed" : "pointer", transition: "all 0.2s" }}
          >
            {loading ? "Authenticating..." : "▶ Login"}
          </button>

          <div style={{ color: "#ffffff20", fontSize: 10, textAlign: "center", marginTop: 16, letterSpacing: 1 }}>
            Default: admin / admin123
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Scanning animation ────────────────────────────────────────────────────────
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
            <div style={{ width: 48, height: 48, background: cfg.bg, border: `1px solid ${cfg.color}44`, borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, color: cfg.color }}>{getDeviceIcon(device.type)}</div>
            <div>
              <div style={{ color: "#fff", fontSize: 15, fontWeight: 700, fontFamily: "monospace" }}>{device.type}</div>
              <div style={{ color: "#ffffff60", fontSize: 11, fontFamily: "monospace" }}>{device.vendor} · {device.mac}</div>
            </div>
          </div>
          <VulnBadge severity={device.status} />
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          {[["IP Address", device.ip], ["Protocol", device.protocol], ["Firmware", device.firmware], ["Open Ports", device.ports?.map(p => p.port).join(", ") || "none"]].map(([k, v]) => (
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
              {device.ports.map(p => <span key={p.port} style={{ background: "#ffffff08", border: "1px solid #ffffff15", borderRadius: 4, padding: "2px 8px", fontSize: 10, color: "#ffffff70", fontFamily: "monospace" }}>{p.port}/{p.service}</span>)}
            </div>
          </div>
        )}
      </div>
      <div style={{ color: "#ffffff50", fontSize: 11, fontFamily: "monospace", letterSpacing: 2, textTransform: "uppercase", marginBottom: 8 }}>Vulnerabilities ({device.vulnerabilities?.length || 0})</div>
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
                    {v.cvss && v.cvss !== "N/A" && <div style={{ marginBottom: 8 }}><span style={{ background: "#ffffff08", border: "1px solid #ffffff15", borderRadius: 4, padding: "2px 8px", fontSize: 10, color: "#ffffff60", fontFamily: "monospace" }}>CVSS {v.cvss}</span></div>}
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
              <div style={{ flex: 1 }}><span style={{ color: "#ffffffcc", fontSize: 12, fontFamily: "monospace" }}>{v.name}</span><span style={{ color: "#ffffff30", fontSize: 11, fontFamily: "monospace" }}> — {v.device}</span></div>
              <span style={{ color: "#ffffff30", fontSize: 10, fontFamily: "monospace" }}>{v.ip}</span>
            </div>
          ))}
        </div>
      </>}
    </div>
  );
}

function HistoryTab({ onLoad, refreshKey, token }) {
  const [history, setHistory]       = useState([]);
  const [loading, setLoading]       = useState(true);
  const [deleting, setDeleting]     = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    setLoading(true);
    fetch(`${API}/api/scans`, { headers }).then(r => r.json()).then(data => { setHistory(data); setLoading(false); }).catch(() => setLoading(false));
  }, [refreshKey]);

  const handleDelete = async (scan_id) => {
    setDeleting(scan_id);
    try { await fetch(`${API}/api/scans/${scan_id}`, { method: "DELETE", headers }); setHistory(prev => prev.filter(s => s.scan_id !== scan_id)); }
    catch { alert("Failed to delete scan."); }
    setDeleting(null); setConfirmDelete(null);
  };

  const handleDeleteAll = async () => {
    setDeleting("all");
    try { await fetch(`${API}/api/scans`, { method: "DELETE", headers }); setHistory([]); }
    catch { alert("Failed to delete all scans."); }
    setDeleting(null); setConfirmDelete(null);
  };

  if (loading) return <div style={{ color: "#ffffff40", fontFamily: "monospace", textAlign: "center", paddingTop: 60 }}>Loading scan history...</div>;
  if (!history.length) return <div style={{ color: "#ffffff30", fontFamily: "monospace", textAlign: "center", paddingTop: 60 }}>No previous scans found.</div>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
        {confirmDelete === "all" ? (
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ color: "#ffffff50", fontSize: 11, fontFamily: "monospace" }}>Delete all scans?</span>
            <button onClick={handleDeleteAll} style={{ background: "#FF3B3B22", border: "1px solid #FF3B3B44", color: "#FF3B3B", borderRadius: 6, padding: "4px 12px", fontSize: 11, cursor: "pointer", fontFamily: "monospace" }}>{deleting === "all" ? "Deleting..." : "Confirm"}</button>
            <button onClick={() => setConfirmDelete(null)} style={{ background: "#ffffff08", border: "1px solid #ffffff15", color: "#ffffff60", borderRadius: 6, padding: "4px 12px", fontSize: 11, cursor: "pointer", fontFamily: "monospace" }}>Cancel</button>
          </div>
        ) : (
          <button onClick={() => setConfirmDelete("all")} style={{ background: "#FF3B3B12", border: "1px solid #FF3B3B33", color: "#FF3B3B88", borderRadius: 6, padding: "5px 14px", fontSize: 11, cursor: "pointer", fontFamily: "monospace", letterSpacing: 1 }}>✕ Clear All History</button>
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
                    <button onClick={() => handleDelete(s.scan_id)} style={{ background: "#FF3B3B22", border: "1px solid #FF3B3B44", color: "#FF3B3B", borderRadius: 6, padding: "4px 10px", fontSize: 10, cursor: "pointer", fontFamily: "monospace" }}>{deleting === s.scan_id ? "..." : "Delete"}</button>
                    <button onClick={() => setConfirmDelete(null)} style={{ background: "#ffffff08", border: "1px solid #ffffff15", color: "#ffffff50", borderRadius: 6, padding: "4px 10px", fontSize: 10, cursor: "pointer", fontFamily: "monospace" }}>Cancel</button>
                  </div>
                ) : (
                  <button onClick={(e) => { e.stopPropagation(); setConfirmDelete(s.scan_id); }} style={{ background: "transparent", border: "1px solid #ffffff15", color: "#ffffff30", borderRadius: 6, padding: "4px 10px", fontSize: 11, cursor: "pointer", fontFamily: "monospace" }}>✕</button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Root App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken]               = useState(() => localStorage.getItem("iot_token") || "");
  const [username, setUsername]         = useState(() => localStorage.getItem("iot_username") || "");
  const [phase, setPhase]               = useState("idle");
  const [scanStage, setScanStage]       = useState("");
  const [scanProgress, setScanProgress] = useState(0);
  const [results, setResults]           = useState(null);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [activeTab, setActiveTab]       = useState("devices");
  const [apiOnline, setApiOnline]       = useState(null);
  const [historyKey, setHistoryKey]     = useState(0);
  const pollRef = useRef(null);

  const authHeaders = { Authorization: `Bearer ${token}` };

  // Check API health and token validity on mount
  useEffect(() => {
    fetch(`${API}/`).then(r => r.json()).then(() => setApiOnline(true)).catch(() => setApiOnline(false));
    if (token) {
      fetch(`${API}/api/auth/me`, { headers: authHeaders })
        .then(r => { if (!r.ok) handleLogout(); })
        .catch(() => {});
    }
  }, []);

  const handleLogin = (newToken, newUsername) => {
    setToken(newToken);
    setUsername(newUsername);
  };

  const handleLogout = () => {
    localStorage.removeItem("iot_token");
    localStorage.removeItem("iot_username");
    setToken(""); setUsername("");
    setPhase("idle"); setResults(null);
  };

  const goHome = () => {
    if (pollRef.current) clearInterval(pollRef.current);
    setPhase("idle"); setResults(null); setSelectedDevice(null);
    setHistoryKey(k => k + 1);
  };

  const startScan = async () => {
    setPhase("scanning"); setScanProgress(0); setScanStage("Initializing...");
    setResults(null); setSelectedDevice(null);
    try {
      const res = await fetch(`${API}/api/scan/start`, { method: "POST", headers: authHeaders });
      if (res.status === 401) { handleLogout(); return; }
      const { scan_id } = await res.json();
      pollRef.current = setInterval(async () => {
        const s = await fetch(`${API}/api/scan/status/${scan_id}`, { headers: authHeaders }).then(r => r.json());
        setScanStage(s.stage || ""); setScanProgress(s.progress || 0);
        if (s.status === "complete") {
          clearInterval(pollRef.current);
          setResults(s.results); setSelectedDevice(s.results.devices?.[0] || null);
          setPhase("results"); setActiveTab("devices"); setHistoryKey(k => k + 1);
        } else if (s.status === "error") {
          clearInterval(pollRef.current); setPhase("idle");
          alert("Scan failed: " + s.error);
        }
      }, 400);
    } catch { setPhase("idle"); alert("Cannot reach backend. Is the API running?"); }
  };

  const loadHistoryScan = async (scan_id) => {
    const data = await fetch(`${API}/api/scans/${scan_id}`, { headers: authHeaders }).then(r => r.json());
    setResults(data); setSelectedDevice(data.devices?.[0] || null);
    setPhase("results"); setActiveTab("devices");
  };

  // Show login page if not authenticated
  if (!token) return <LoginPage onLogin={handleLogin} />;

  const criticalCount = results?.severity_counts?.critical || 0;
  const highCount     = results?.severity_counts?.high     || 0;

  return (
    <div style={{ minHeight: "100vh", width: "100vw", background: "#080c12", color: "#fff", fontFamily: "monospace", position: "relative", overflowX: "hidden" }}>
      <style>{`
        @keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
        @keyframes spin{from{transform:rotate(0)}to{transform:rotate(360deg)}}
        @keyframes spinR{from{transform:rotate(360deg)}to{transform:rotate(0)}}
        ::-webkit-scrollbar{width:4px} ::-webkit-scrollbar-thumb{background:#ffffff20;border-radius:2px}
        *{box-sizing:border-box;margin:0;padding:0} html,body{margin:0;padding:0;width:100vw;max-width:100%;overflow-x:hidden}
      `}</style>
      <div style={{ position: "fixed", inset: 0, backgroundImage: "linear-gradient(#00ffcc04 1px,transparent 1px),linear-gradient(90deg,#00ffcc04 1px,transparent 1px)", backgroundSize: "40px 40px", pointerEvents: "none", zIndex: 0 }} />
      <div style={{ position: "fixed", inset: 0, background: "radial-gradient(ellipse at 20% 20%,#00ffcc08,transparent 60%),radial-gradient(ellipse at 80% 80%,#0044ff06,transparent 60%)", pointerEvents: "none", zIndex: 0 }} />

      <div style={{ position: "relative", zIndex: 1, padding: "24px 32px" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 28 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            {phase !== "idle" && (
              <button onClick={goHome} style={{ background: "#ffffff08", border: "1px solid #ffffff18", color: "#ffffff70", borderRadius: 8, padding: "7px 16px", fontSize: 12, cursor: "pointer", fontFamily: "monospace", letterSpacing: 1 }}>← Home</button>
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
                  <div key={sev} style={{ background: SEVERITY_CONFIG[sev].bg, border: `1px solid ${SEVERITY_CONFIG[sev].color}44`, borderRadius: 6, padding: "4px 12px", fontSize: 11, color: SEVERITY_CONFIG[sev].color }}>{label}</div>
                ))}
              </div>
            )}
            {/* Logged in user + logout */}
            <div style={{ display: "flex", alignItems: "center", gap: 8, background: "#ffffff08", border: "1px solid #ffffff12", borderRadius: 8, padding: "6px 12px" }}>
              <span style={{ color: "#00ffcc", fontSize: 11, fontFamily: "monospace" }}>⊛ {username}</span>
              <span style={{ color: "#ffffff20" }}>|</span>
              <button onClick={handleLogout} style={{ background: "transparent", border: "none", color: "#FF3B3B88", fontSize: 11, cursor: "pointer", fontFamily: "monospace", padding: 0 }}>Logout</button>
            </div>
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
            <HistoryTab onLoad={loadHistoryScan} refreshKey={historyKey} token={token} />
          </div>
        )}

        {/* SCANNING */}
        {phase === "scanning" && <ScanningOverlay stage={scanStage} progress={scanProgress} />}

        {/* RESULTS */}
        {phase === "results" && results && (
          <div style={{ animation: "fadeIn 0.4s ease" }}>
            <div style={{ display: "flex", gap: 4, marginBottom: 18 }}>
              {[["devices", `⊞  Devices (${results.devices_found})`], ["report", "≡  Risk Report"], ["history", "⊕  History"]].map(([tab, label]) => (
                <button key={tab} onClick={() => setActiveTab(tab)} style={{ background: activeTab === tab ? "#ffffff0f" : "transparent", border: `1px solid ${activeTab === tab ? "#ffffff22" : "transparent"}`, borderBottom: activeTab === tab ? "1px solid #00ffcc66" : "1px solid transparent", color: activeTab === tab ? "#fff" : "#ffffff40", borderRadius: "8px 8px 0 0", padding: "8px 18px", fontSize: 12, cursor: "pointer", fontFamily: "monospace", letterSpacing: 1, transition: "all 0.2s" }}>{label}</button>
              ))}
              <div style={{ flex: 1, borderBottom: "1px solid #ffffff10" }} />
              <div style={{ display: "flex", alignItems: "center", paddingRight: 4, borderBottom: "1px solid #ffffff10" }}>
                <span style={{ color: "#ffffff30", fontSize: 11, fontFamily: "monospace" }}>{results.total_vulnerabilities} vulns · {results.devices_found} devices · {new Date(results.scan_time).toLocaleTimeString()}</span>
              </div>
            </div>

            {activeTab === "devices" && (
              <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 16, height: "calc(100vh - 200px)" }}>
                <div style={{ display: "flex", flexDirection: "column", gap: 8, overflowY: "auto" }}>
                  {results.devices.map((d, i) => <DeviceCard key={i} device={d} selected={selectedDevice?.ip === d.ip} onClick={() => setSelectedDevice(d)} />)}
                </div>
                <div style={{ background: "#ffffff04", border: "1px solid #ffffff0d", borderRadius: 14, padding: 20, overflowY: "auto" }}>
                  {selectedDevice ? <DeviceDetail device={selectedDevice} /> : <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "#ffffff20", fontSize: 13 }}>← Select a device</div>}
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
                <HistoryTab onLoad={loadHistoryScan} refreshKey={historyKey} token={token} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
