@echo off
echo ========================================================
echo        STARTING SKILLTRACE DEMO (SIH 2026)
echo ========================================================
echo [1/2] Verifying database seeding...
python -m backend.database.seed_data
echo [2/2] Launching SKILLTRACE Server at http://127.0.0.1:8000...
echo --------------------------------------------------------
echo Access the application in your browser:
echo   - Web Dashboard:  http://127.0.0.1:8000
echo   - Pre-Assessment: http://127.0.0.1:8000/assessment.html
echo   - Swagger Docs:   http://127.0.0.1:8000/docs
echo --------------------------------------------------------
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
