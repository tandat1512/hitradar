@echo off
REM Start HitRadar Pro FastAPI Backend
REM Usage: run.bat [port]
set PORT=%1
if "%PORT%"=="" set PORT=8000

echo Starting HitRadar Pro API on http://127.0.0.1:%PORT%
echo.
python -m uvicorn api:app --host 127.0.0.1 --port %PORT% --reload
