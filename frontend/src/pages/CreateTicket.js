import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createTicket } from "../services/api";

const CATEGORIES = [
  "VPN Issue", "Password Reset", "Software Installation",
  "Laptop Issue", "Email Access", "Network Connectivity",
  "Hardware Request", "Other",
];

const PRIORITIES = ["Low", "Medium", "High", "Critical"];

const DEPARTMENTS = [
  "IT", "Finance", "HR", "Operations", "Marketing",
  "Sales", "Legal", "Engineering", "Customer Support",
];

export default function CreateTicket() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    employee_name: "",
    department: "",
    issue_category: "",
    description: "",
    priority: "Medium",
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const validate = () => {
    const e = {};
    if (!form.employee_name.trim()) e.employee_name = "Employee name is required.";
    if (!form.department) e.department = "Department is required.";
    if (!form.issue_category) e.issue_category = "Issue category is required.";
    if (!form.description.trim() || form.description.trim().length < 10)
      e.description = "Description must be at least 10 characters.";
    if (!form.priority) e.priority = "Priority is required.";
    return e;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validation = validate();
    if (Object.keys(validation).length > 0) { setErrors(validation); return; }
    setSubmitting(true);
    setErrorMsg("");
    try {
      const res = await createTicket(form);
      setSuccessMsg(`Ticket #${res.data.ticket_id} created successfully!`);
      setTimeout(() => navigate(`/tickets/${res.data.ticket_id}`), 1500);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || "Failed to create ticket.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">Create New Ticket</h1>
      <div className="card" style={{ maxWidth: 700 }}>
        {successMsg && <div className="alert alert-success">{successMsg}</div>}
        {errorMsg && <div className="alert alert-error">{errorMsg}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="employee_name">Employee Name *</label>
              <input
                id="employee_name" name="employee_name" type="text"
                placeholder="John Doe"
                value={form.employee_name} onChange={handleChange}
              />
              {errors.employee_name && <span style={{ color: "#f44336", fontSize: "0.78rem" }}>{errors.employee_name}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="department">Department *</label>
              <select id="department" name="department" value={form.department} onChange={handleChange}>
                <option value="">-- Select --</option>
                {DEPARTMENTS.map((d) => <option key={d}>{d}</option>)}
              </select>
              {errors.department && <span style={{ color: "#f44336", fontSize: "0.78rem" }}>{errors.department}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="issue_category">Issue Category *</label>
              <select id="issue_category" name="issue_category" value={form.issue_category} onChange={handleChange}>
                <option value="">-- Select --</option>
                {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
              </select>
              {errors.issue_category && <span style={{ color: "#f44336", fontSize: "0.78rem" }}>{errors.issue_category}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="priority">Priority *</label>
              <select id="priority" name="priority" value={form.priority} onChange={handleChange}>
                {PRIORITIES.map((p) => <option key={p}>{p}</option>)}
              </select>
              {errors.priority && <span style={{ color: "#f44336", fontSize: "0.78rem" }}>{errors.priority}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description *</label>
            <textarea
              id="description" name="description" rows={4}
              placeholder="Describe the issue in detail (at least 10 characters)..."
              value={form.description} onChange={handleChange}
            />
            {errors.description && <span style={{ color: "#f44336", fontSize: "0.78rem" }}>{errors.description}</span>}
          </div>

          <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? "Submitting..." : "Submit Ticket"}
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => navigate("/tickets")}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
