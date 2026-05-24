# Helpdesk Ticket Management System (HDMS)

> **Capstone Project — Phase 1**  
> A full-stack web application for managing internal employee IT support tickets.

---

## Project Overview

Modern organizations handle employee IT issues (VPN failures, password resets, software requests, etc.) through scattered emails and spreadsheets. **HDMS** centralizes this process with a clean web interface, a REST API, and an ETL pipeline for data engineering workflows.

**Tech Stack**

| Layer       | Technology              |
|-------------|-------------------------|
| Frontend    | React 18, React Router  |
| Backend     | Python FastAPI          |
| Database    | SQLite (via SQLAlchemy) |
| ETL         | Python (pandas, custom) |
| API Testing | Postman / Swagger UI    |
| Version Control | Git / GitHub        |

---

## Features

- **Create** support tickets with employee name, department, category, priority
- **View** all tickets with tabular listing and detail view
- **Update** ticket status, priority, and resolution notes
- **Delete** tickets
- **Search** by keyword; filter by status, category, priority
- **Dashboard** with aggregate stats (open, in-progress, resolved, critical counts)
- **ETL Pipeline** — Extract → Transform → Load with SLA breach detection

---

## Project Structure

```
Helpdesk-Ticket-Management-System/
├── backend/
│   ├── main.py            # FastAPI app entry point
│   ├── database.py        # SQLAlchemy engine & session
│   ├── models.py          # ORM Ticket model
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── crud.py            # DB CRUD operations
│   ├── routers/
│   │   └── tickets.py     # Ticket API router
│   ├── services/
│   │   └── etl_service.py # ETL FastAPI router
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/         # Dashboard, TicketList, TicketDetail, CreateTicket, ETLPanel
│   │   ├── services/
│   │   │   └── api.js     # Axios API client
│   │   ├── App.js
│   │   └── App.css
│   ├── public/
│   └── package.json
├── etl/
│   ├── extract.py         # Extract from DB / CSV / JSON
│   ├── transform.py       # Validate, normalize, enrich, deduplicate
│   ├── load.py            # Load to DB / CSV / JSON
│   └── etl_pipeline.py    # CLI orchestrator
├── database/
│   └── schema.sql         # SQL schema + seed data
├── docs/
├── screenshots/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Backend Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Start the FastAPI server
uvicorn backend.main:app --reload
```

Backend runs at: **http://localhost:8000**  
Interactive API docs: **http://localhost:8000/docs**

### Frontend Setup

```bash
# 1. Install Node dependencies
cd frontend
npm install

# 2. Start React dev server
npm start
```

Frontend runs at: **http://localhost:3000**

### Database

SQLite database (`helpdesk.db`) is auto-created on first backend run.  
To load seed data manually:

```bash
sqlite3 backend/helpdesk.db < database/schema.sql
```

---

## API Endpoints

| Method | Endpoint         | Description              |
|--------|-----------------|--------------------------|
| GET    | /               | Health check             |
| GET    | /dashboard      | Dashboard statistics     |
| GET    | /tickets/       | List all tickets         |
| GET    | /tickets/{id}   | Get ticket by ID         |
| POST   | /tickets/       | Create ticket            |
| PUT    | /tickets/{id}   | Update ticket            |
| DELETE | /tickets/{id}   | Delete ticket            |
| GET    | /search         | Search/filter tickets    |
| POST   | /etl/run/sync   | Run ETL pipeline (sync)  |
| GET    | /etl/status     | Last ETL run status      |

---

## ETL Pipeline

The ETL pipeline can be triggered via CLI or HTTP API.

### CLI Usage

```bash
# Export DB tickets to CSV
python -m etl.etl_pipeline --source db --target csv

# Import tickets from CSV into DB
python -m etl.etl_pipeline --source csv --input data/raw.csv --target db

# Dry run (no load)
python -m etl.etl_pipeline --source db --dry-run
```

### ETL Stages

1. **Extract** — Pull data from SQLite DB, CSV, or JSON file
2. **Transform** — Validate required fields, normalize text, standardize enums, enrich with `age_days` and `sla_breached` flag, deduplicate
3. **Load** — Write to DB (upsert), CSV export, or JSON export

---

## Git Push Instructions

```bash
# Initialize repository (first time)
git init
git remote add origin https://github.com/<your-username>/AFDE_<YourName>_HDMS.git

# Stage and commit
git add .
git commit -m "Initial commit: Helpdesk Ticket Management System Phase 1"

# Push
git push -u origin main
```

### Recommended Branch Strategy

```bash
git checkout -b feature/backend-api
git checkout -b feature/frontend-ui
git checkout -b feature/etl-pipeline
```

---

## Ticket Schema

| Column           | Type     | Description                         |
|-----------------|----------|-------------------------------------|
| ticket_id        | Integer  | Auto-incremented primary key        |
| employee_name    | String   | Name of the employee                |
| department       | String   | Employee's department               |
| issue_category   | String   | Category of the issue               |
| description      | Text     | Detailed issue description          |
| priority         | String   | Low / Medium / High / Critical      |
| status           | String   | Open / In Progress / Resolved / Closed |
| resolution_notes | Text     | Support admin resolution notes      |
| created_at       | DateTime | Ticket creation timestamp           |

---

## Evaluation Criteria

| Criteria                 | Weightage |
|--------------------------|-----------|
| Frontend Development     | 20%       |
| Backend API Development  | 25%       |
| Database Integration     | 15%       |
| CRUD Functionality       | 15%       |
| UI/UX Design             | 10%       |
| Code Structure & Standards | 10%     |
| Documentation            | 5%        |
