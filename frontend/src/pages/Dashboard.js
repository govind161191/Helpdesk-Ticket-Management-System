import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard } from "../services/api";

const statusBadge = (s) => {
  const map = { Open: "Open", "In Progress": "InProgress", Resolved: "Resolved", Closed: "Closed" };
  return <span className={`badge badge-${map[s] || "Open"}`}>{s}</span>;
};

const priorityBadge = (p) => (
  <span className={`badge badge-${p}`}>{p}</span>
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard()
      .then((res) => { setStats(res.data); setLoading(false); })
      .catch(() => { setError("Failed to load dashboard. Is the backend running?"); setLoading(false); });
  }, []);

  if (loading) return <div className="loader">Loading dashboard...</div>;
  if (error) return <div className="alert alert-error">{error}</div>;

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>

      {/* ── Stat cards ── */}
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total}</div>
          <div className="stat-label">Total Tickets</div>
        </div>
        <div className="stat-card open">
          <div className="stat-value">{stats.open}</div>
          <div className="stat-label">Open</div>
        </div>
        <div className="stat-card prog">
          <div className="stat-value">{stats.in_progress}</div>
          <div className="stat-label">In Progress</div>
        </div>
        <div className="stat-card res">
          <div className="stat-value">{stats.resolved}</div>
          <div className="stat-label">Resolved</div>
        </div>
        <div className="stat-card closed">
          <div className="stat-value">{stats.closed}</div>
          <div className="stat-label">Closed</div>
        </div>
        <div className="stat-card crit">
          <div className="stat-value">{stats.critical}</div>
          <div className="stat-label">Critical</div>
        </div>
      </div>

      {/* ── Recent tickets ── */}
      <div className="card">
        <h2 style={{ marginBottom: "1rem", fontSize: "1.1rem" }}>Recent Tickets</h2>
        {stats.recent_tickets.length === 0 ? (
          <p style={{ color: "#999" }}>No tickets yet. <Link to="/create">Create one!</Link></p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Employee</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_tickets.map((t) => (
                  <tr key={t.ticket_id}>
                    <td>{t.ticket_id}</td>
                    <td>{t.employee_name}</td>
                    <td>{t.issue_category}</td>
                    <td>{priorityBadge(t.priority)}</td>
                    <td>{statusBadge(t.status)}</td>
                    <td>{t.created_at ? new Date(t.created_at).toLocaleDateString() : "—"}</td>
                    <td>
                      <Link to={`/tickets/${t.ticket_id}`} className="btn btn-primary btn-sm">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div style={{ marginTop: "1rem" }}>
          <Link to="/tickets" className="btn btn-primary">View All Tickets</Link>
          &nbsp;
          <Link to="/create" className="btn btn-success" style={{ marginLeft: "0.5rem" }}>+ New Ticket</Link>
        </div>
      </div>
    </div>
  );
}
