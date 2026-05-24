import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import TicketList from "./pages/TicketList";
import CreateTicket from "./pages/CreateTicket";
import TicketDetail from "./pages/TicketDetail";
import ETLPanel from "./pages/ETLPanel";
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app">
        {/* ── Navbar ── */}
        <nav className="navbar">
          <div className="navbar-brand">
            <span className="brand-icon">🎫</span>
            <span>Helpdesk HDMS</span>
          </div>
          <ul className="nav-links">
            <li><NavLink to="/" end>Dashboard</NavLink></li>
            <li><NavLink to="/tickets">Tickets</NavLink></li>
            <li><NavLink to="/create">New Ticket</NavLink></li>
            <li><NavLink to="/etl">ETL Pipeline</NavLink></li>
          </ul>
        </nav>

        {/* ── Page content ── */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tickets" element={<TicketList />} />
            <Route path="/tickets/:id" element={<TicketDetail />} />
            <Route path="/create" element={<CreateTicket />} />
            <Route path="/etl" element={<ETLPanel />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>Helpdesk Ticket Management System &mdash; Phase 1 &copy; 2026</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
