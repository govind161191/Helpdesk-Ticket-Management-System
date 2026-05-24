import React, { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { getTickets, searchTickets, deleteTicket } from "../services/api";

const STATUSES = ["", "Open", "In Progress", "Resolved", "Closed"];
const CATEGORIES = ["", "VPN Issue", "Password Reset", "Software Installation",
  "Laptop Issue", "Email Access", "Network Connectivity", "Hardware Request", "Other"];
const PRIORITIES = ["", "Low", "Medium", "High", "Critical"];

const statusClass = (s) => {
  const m = { Open: "Open", "In Progress": "InProgress", Resolved: "Resolved", Closed: "Closed" };
  return `badge badge-${m[s] || "Open"}`;
};

export default function TicketList() {
  const [tickets, setTickets] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [keyword, setKeyword] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [priority, setPriority] = useState("");

  const [deleteMsg, setDeleteMsg] = useState("");

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      let res;
      if (keyword.trim()) {
        res = await searchTickets({ keyword, status: status || undefined, category: category || undefined, priority: priority || undefined });
      } else {
        res = await getTickets({ status: status || undefined, category: category || undefined, priority: priority || undefined });
      }
      setTickets(res.data.tickets);
      setTotal(res.data.total);
    } catch {
      setError("Failed to load tickets.");
    } finally {
      setLoading(false);
    }
  }, [keyword, status, category, priority]);

  useEffect(() => { fetchTickets(); }, [fetchTickets]);

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete Ticket #${id}?`)) return;
    try {
      await deleteTicket(id);
      setDeleteMsg(`Ticket #${id} deleted.`);
      fetchTickets();
    } catch {
      setDeleteMsg("Failed to delete ticket.");
    }
  };

  return (
    <div>
      <h1 className="page-title">All Tickets {total > 0 && <span style={{ fontSize: "1rem", color: "#666" }}>({total})</span>}</h1>

      {deleteMsg && <div className="alert alert-info">{deleteMsg}</div>}

      {/* ── Filters ── */}
      <div className="filters card" style={{ marginBottom: "1.25rem" }}>
        <input
          type="text" placeholder="Search keyword..."
          value={keyword} onChange={(e) => setKeyword(e.target.value)}
          style={{ flex: 2 }}
        />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {STATUSES.map((s) => <option key={s} value={s}>{s || "All Statuses"}</option>)}
        </select>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c || "All Categories"}</option>)}
        </select>
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          {PRIORITIES.map((p) => <option key={p} value={p}>{p || "All Priorities"}</option>)}
        </select>
        <Link to="/create" className="btn btn-success">+ New Ticket</Link>
      </div>

      {loading && <div className="loader">Loading tickets...</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {!loading && !error && (
        <div className="card">
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Employee</th>
                  <th>Dept</th>
                  <th>Category</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tickets.length === 0 ? (
                  <tr><td colSpan={8} style={{ textAlign: "center", color: "#999", padding: "2rem" }}>
                    No tickets found. <Link to="/create">Create one!</Link>
                  </td></tr>
                ) : tickets.map((t) => (
                  <tr key={t.ticket_id}>
                    <td>{t.ticket_id}</td>
                    <td>{t.employee_name}</td>
                    <td>{t.department}</td>
                    <td>{t.issue_category}</td>
                    <td><span className={`badge badge-${t.priority}`}>{t.priority}</span></td>
                    <td><span className={statusClass(t.status)}>{t.status}</span></td>
                    <td>{t.created_at ? new Date(t.created_at).toLocaleDateString() : "—"}</td>
                    <td style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                      <Link to={`/tickets/${t.ticket_id}`} className="btn btn-primary btn-sm">View</Link>
                      <button className="btn btn-danger btn-sm" onClick={() => handleDelete(t.ticket_id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
