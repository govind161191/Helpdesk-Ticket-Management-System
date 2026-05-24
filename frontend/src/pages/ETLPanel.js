import React, { useState } from "react";
import { runETL, getETLStatus } from "../services/api";

export default function ETLPanel() {
  const [source, setSource] = useState("db");
  const [target, setTarget] = useState("csv");
  const [dryRun, setDryRun] = useState(false);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleRun = async () => {
    setRunning(true);
    setError("");
    setResult(null);
    try {
      const res = await runETL({ source, target, dry_run: dryRun });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "ETL pipeline failed.");
    } finally {
      setRunning(false);
    }
  };

  const handleStatus = async () => {
    try {
      const res = await getETLStatus();
      setResult(res.data);
    } catch {
      setError("Failed to fetch ETL status.");
    }
  };

  const logText = result?.result?.summary?.stages?.join("\n") || "";

  return (
    <div>
      <h1 className="page-title">ETL Pipeline</h1>

      <div className="card" style={{ maxWidth: 700, marginBottom: "1.5rem" }}>
        <h2 style={{ fontSize: "1rem", marginBottom: "1rem", color: "#1976d2" }}>Configure & Run Pipeline</h2>
        <p style={{ color: "#666", marginBottom: "1rem", fontSize: "0.9rem" }}>
          The ETL pipeline <strong>Extracts</strong> ticket data, <strong>Transforms</strong> (validates, normalises,
          enriches with SLA breach flags), and <strong>Loads</strong> results to the selected target.
        </p>

        <div className="form-grid">
          <div className="form-group">
            <label>Source</label>
            <select value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="db">Database (SQLite)</option>
              <option value="csv">CSV File</option>
              <option value="json">JSON File</option>
            </select>
          </div>
          <div className="form-group">
            <label>Target</label>
            <select value={target} onChange={(e) => setTarget(e.target.value)}>
              <option value="csv">CSV Export</option>
              <option value="json">JSON Export</option>
              <option value="db">Database (upsert)</option>
              <option value="all">All (DB + CSV + JSON)</option>
            </select>
          </div>
        </div>

        <div className="form-group" style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <input type="checkbox" id="dryRun" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} style={{ width: "auto" }} />
          <label htmlFor="dryRun" style={{ marginBottom: 0 }}>Dry Run (extract + transform only, skip load)</label>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
          <button className="btn btn-primary" onClick={handleRun} disabled={running}>
            {running ? "Running..." : "▶ Run Pipeline"}
          </button>
          <button className="btn btn-secondary" onClick={handleStatus}>
            Refresh Status
          </button>
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div className="card">
          <h2 style={{ fontSize: "1rem", marginBottom: "0.75rem" }}>Pipeline Result</h2>
          <div className="stat-grid" style={{ marginBottom: "1rem" }}>
            {result.result?.extracted !== undefined && (
              <div className="stat-card"><div className="stat-value">{result.result.extracted}</div><div className="stat-label">Extracted</div></div>
            )}
            {result.result?.valid !== undefined && (
              <div className="stat-card res"><div className="stat-value">{result.result.valid}</div><div className="stat-label">Valid</div></div>
            )}
            {result.result?.rejected !== undefined && (
              <div className="stat-card crit"><div className="stat-value">{result.result.rejected}</div><div className="stat-label">Rejected</div></div>
            )}
          </div>
          <div style={{ marginBottom: "0.5rem", fontSize: "0.85rem" }}>
            <strong>Status:</strong> {result.status} &nbsp;|&nbsp; <strong>Message:</strong> {result.message}
          </div>
          {logText && (
            <>
              <div style={{ fontWeight: 600, marginBottom: "0.4rem", fontSize: "0.85rem" }}>Pipeline Log</div>
              <div className="log-box">{logText}</div>
            </>
          )}
          {result.result?.exported_csv && (
            <div className="alert alert-success" style={{ marginTop: "0.75rem" }}>
              CSV exported to: <code>{result.result.exported_csv}</code>
            </div>
          )}
          {result.result?.exported_json && (
            <div className="alert alert-success" style={{ marginTop: "0.5rem" }}>
              JSON exported to: <code>{result.result.exported_json}</code>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
