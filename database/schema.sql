-- =====================================================
-- Helpdesk Ticket Management System — Database Schema
-- Database: SQLite (compatible with PostgreSQL)
-- =====================================================

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name   VARCHAR(100) NOT NULL,
    department      VARCHAR(100) NOT NULL,
    issue_category  VARCHAR(100) NOT NULL,
    description     TEXT         NOT NULL,
    priority        VARCHAR(20)  NOT NULL DEFAULT 'Medium',  -- Low | Medium | High | Critical
    status          VARCHAR(20)  NOT NULL DEFAULT 'Open',    -- Open | In Progress | Resolved | Closed
    resolution_notes TEXT,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME
);

-- Indexes for commonly filtered columns
CREATE INDEX IF NOT EXISTS idx_tickets_status    ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority  ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_category  ON tickets(issue_category);
CREATE INDEX IF NOT EXISTS idx_tickets_employee  ON tickets(employee_name);

-- ── Sample seed data ──────────────────────────────────────────────────────────
INSERT OR IGNORE INTO tickets (employee_name, department, issue_category, description, priority, status)
VALUES
    ('Alice Johnson',   'IT',        'VPN Issue',            'Cannot connect to corporate VPN from home.',      'High',     'Open'),
    ('Bob Smith',       'Finance',   'Password Reset',       'Account locked after multiple failed attempts.',  'Medium',   'In Progress'),
    ('Clara Evans',     'HR',        'Software Installation','Adobe Acrobat Pro needed for HR documentation.',  'Low',      'Open'),
    ('David Kumar',     'Engineering','Laptop Issue',        'Laptop battery not charging, battery light off.', 'Critical', 'Open'),
    ('Eva Martinez',    'Sales',     'Email Access',         'Cannot access shared mailbox since this morning.','High',     'Resolved');
