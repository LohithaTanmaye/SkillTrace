Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       STARTING SKILLTRACE DEMO (SIH 2026)             " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "[1/2] Verifying database seeding..." -ForegroundColor Yellow
python -m backend.database.seed_data

Write-Host "[2/2] Launching SKILLTRACE Server at http://127.0.0.1:8000..." -ForegroundColor Green
Write-Host "--------------------------------------------------------"
Write-Host "Access the application in your browser:"
Write-Host "  - Web Dashboard:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  - Pre-Assessment: http://127.0.0.1:8000/assessment.html" -ForegroundColor Cyan
Write-Host "  - Swagger Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
