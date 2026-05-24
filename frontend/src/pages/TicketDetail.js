import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTicketById, updateTicket, deleteTicket } from "../services/api";

const STATUSES = ["Open", "In Progress", "Resolved", "Closed"];
const PRIORITIES = ["Low", "Medium", "High", "Critical"];

export default function TicketDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");

  useEffect(() => {
    getTicketById(id)
      .then((res) => { setTicket(res.data); setForm(res.data); setLoading(false); })
      .catch(() => { setError("Ticket not found."); setLoading(false); });
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg("");
    try {
      const res = await updateTicket(id, {
        status: form.status,
        priority: form.priority,
        resolution_notes: form.resolution_notes,
        description: form.description,
      });
      setTicket(res.data);
      setForm(res.data);
      setSaveMsg("Ticket updated successfully!");
      setEditing(false);
    } catch {
      setSaveMsg("Failed to update ticket.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Delete this ticket permanently?")) return;
    await deleteTicket(id);
    navigate("/tickets");
  };

  if (loading) return <div className="loader">Loading ticket...</div>;
  if (error) return <div className="alert alert-error">{error}</div>;

  const statusMap = { Open: "Open", "In Progress": "InProgress", Resolved: "Resolved", Closed: "Closed" };

  return (
    <div>
      <h1 className="page-title">Ticket #{ticket.ticket_id}</h1>

      {saveMsg && <div className={`alert ${saveMsg.includes("success") ? "alert-success" : "alert-error"}`}>{saveMsg}</div>}

      <div className="card" style={{ maxWidth: 750 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <span className={`badge badge-${ticket.priority}`}>{ticket.priority}</span>
            <span className={`badge badge-${statusMap[ticket.status]}`}>{ticket.status}</span>
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {!editing && <button className="btn btn-warning" onClick={() => setEditing(true)}>Edit</button>}
            <button className="btn btn-danger" onClick={handleDelete}>Delete</button>
          </div>
        </div>

        <table style={{ width: "100%", marginBottom: "1rem" }}>
          <tbody>
            <tr><td style={{ width: 160, color: "#666", paddingBottom: "0.6rem" }}>Employee</td><td><strong>{ticket.employee_name}</strong></td></tr>
            <tr><td style={{ color: "#666", paddingBottom: "0.6rem" }}>Department</td><td>{ticket.department}</td></tr>
            <tr><td style={{ color: "#666", paddingBottom: "0.6rem" }}>Category</td><td>{ticket.issue_category}</td></tr>
            <tr><td style={{ color: "#666", paddingBottom: "0.6rem" }}>Created</td><td>{ticket.created_at ? new Date(ticket.created_at).toLocaleString() : "—"}</td></tr>
          </tbody>
        </table>

        {editing ? (
          <>
            <div className="form-group">
              <label>Description</label>
              <textarea name="description" rows={3} value={form.description || ""} onChange={handleChange} />
            </div>
            <div className="form-grid">
              <div className="form-group">
                <label>Status</label>
                <select name="status" value={form.status} onChange={handleChange}>
                  {STATUSES.map((s) => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select name="priority" value={form.priority} onChange={handleChange}>
                  {PRIORITIES.map((p) => <option key={p}>{p}</option>)}
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Resolution Notes</label>
              <textarea name="resolution_notes" rows={3} placeholder="Describe the resolution..." value={form.resolution_notes || ""} onChange={handleChange} />
            </div>
            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>{saving ? "Saving..." : "Save Changes"}</button>
              <button className="btn btn-secondary" onClick={() => { setEditing(false); setForm(ticket); }}>Cancel</button>
            </div>
          </>
        ) : (
          <>
            <div style={{ marginBottom: "0.75rem" }}>
              <div style={{ color: "#666", fontSize: "0.82rem", marginBottom: "0.3rem" }}>Description</div>
              <p style={{ lineHeight: 1.6 }}>{ticket.description}</p>
            </div>
            {ticket.resolution_notes && (
              <div style={{ background: "#e8f5e9", borderRadius: 6, padding: "0.75rem", marginTop: "0.75rem" }}>
                <div style={{ color: "#2e7d32", fontWeight: 600, fontSize: "0.82rem", marginBottom: "0.3rem" }}>Resolution Notes</div>
                <p style={{ lineHeight: 1.6 }}>{ticket.resolution_notes}</p>
              </div>
            )}
          </>
        )}
      </div>

      <button className="btn btn-secondary" style={{ marginTop: "1rem" }} onClick={() => navigate("/tickets")}>
        ← Back to Tickets
      </button>
    </div>
  );
}
