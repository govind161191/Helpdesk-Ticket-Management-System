/**
 * api.js — Axios HTTP client configured for the FastAPI backend.
 * Base URL: http://localhost:8000
 */
import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

// ─── Ticket API ───────────────────────────────────────────────────────────────

/** Fetch all tickets with optional filters */
export const getTickets = (params = {}) => API.get("/tickets/", { params });

/** Fetch a single ticket by ID */
export const getTicketById = (id) => API.get(`/tickets/${id}`);

/** Create a new ticket */
export const createTicket = (data) => API.post("/tickets/", data);

/** Update an existing ticket */
export const updateTicket = (id, data) => API.put(`/tickets/${id}`, data);

/** Delete a ticket */
export const deleteTicket = (id) => API.delete(`/tickets/${id}`);

// ─── Search API ───────────────────────────────────────────────────────────────

/** Search tickets by keyword and/or filters */
export const searchTickets = (params = {}) => API.get("/search", { params });

// ─── Dashboard API ────────────────────────────────────────────────────────────

/** Fetch dashboard statistics */
export const getDashboard = () => API.get("/dashboard");

// ─── ETL API ──────────────────────────────────────────────────────────────────

/** Trigger ETL pipeline (sync) */
export const runETL = (params = {}) => API.post("/etl/run/sync", params);

/** Get last ETL pipeline status */
export const getETLStatus = () => API.get("/etl/status");

export default API;
