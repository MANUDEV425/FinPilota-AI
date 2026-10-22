@echo off
REM FinancePilot AI - Startup Script for Windows

echo Starting FinancePilot AI...
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Please edit .env and add your GEMINI_API_KEY if desired
    echo.
)

REM Start ML Service
echo Starting ML Service on port 8000...
cd ml
call venv\Scripts\activate
start "ML Service" cmd /k "uvicorn api:app --host 0.0.0.0 --port 8000"
cd ..
echo ML Service started
echo.

REM Wait for ML service to be ready
echo Waiting for ML service to be ready...
timeout /t 3 /nobreak

REM Start Express Backend
echo Starting Express Backend on port 3001...
start "Express Backend" cmd /k "set PORT=3001 && set ML_SERVICE_URL=http://localhost:8000 && node server/index.cjs"
echo Express Backend started
echo.

REM Wait for API to be ready
echo Waiting for API to be ready...
timeout /t 2 /nobreak

REM Start React Frontend
echo Starting React Frontend on port 5173...
start "React Frontend" cmd /k "npm run dev"
echo React Frontend started
echo.

echo ==========================================
echo FinancePilot AI is now running!
echo ==========================================
echo.
echo Frontend: http://localhost:5173
echo API: http://localhost:3001
echo ML Service: http://localhost:8000
echo.
echo Close the terminal windows to stop services
pause
