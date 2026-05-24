@echo off
REM ============================================================
REM  Helpdesk Ticket Management System — Git Setup & Push Script
REM  Run this ONCE from inside the project folder.
REM  Usage:  git_setup.bat <your-github-username>
REM ============================================================

SET USERNAME=%1

IF "%USERNAME%"=="" (
    echo ERROR: Please provide your GitHub username.
    echo Usage: git_setup.bat ^<your-github-username^>
    pause
    exit /b 1
)

echo ==========================================
echo  Step 1: Initialize Git repository
echo ==========================================
git init
git config user.name "Govind Kumar"
git config user.email "govindkumar.v@prodapt.com"

echo ==========================================
echo  Step 2: Stage all files
echo ==========================================
git add .

echo ==========================================
echo  Step 3: Initial commit
echo ==========================================
git commit -m "Initial commit: Helpdesk Ticket Management System - Phase 1

- FastAPI backend with full CRUD, search, and dashboard endpoints
- SQLAlchemy ORM with SQLite database integration
- Pydantic v2 request/response schemas
- ETL pipeline: extract (DB/CSV/JSON), transform (validate/normalize/enrich/deduplicate), load (DB/CSV/JSON)
- ETL API endpoint: POST /etl/run/sync, GET /etl/status
- React frontend: Dashboard, TicketList, TicketDetail, CreateTicket, ETLPanel
- Axios HTTP client configured for all API endpoints
- Database schema.sql with seed data
- README.md with full setup, API docs, git push instructions
- .gitignore for Python, Node, SQLite"

echo ==========================================
echo  Step 4: Rename branch to main
echo ==========================================
git branch -M main

echo ==========================================
echo  Step 5: Add GitHub remote
echo  Repository: AFDE_Govind_HDMS
echo ==========================================
git remote add origin https://github.com/%USERNAME%/AFDE_Govind_HDMS.git

echo ==========================================
echo  Step 6: Push to GitHub
echo ==========================================
git push -u origin main

echo.
echo ==========================================
echo  DONE! Your code is now on GitHub.
echo  Visit: https://github.com/%USERNAME%/AFDE_Govind_HDMS
echo ==========================================
pause
