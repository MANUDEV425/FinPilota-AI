@echo off
REM ============================================================================
REM FinPilot AI - Fetch.ai Multi-Agent Launch Script (ASI:One / Hackathon)
REM ============================================================================

echo ============================================================================
echo Starting FinPilot AI Fetch.ai Agent Network...
echo ============================================================================
echo.

cd /d "%~dp0"

REM Detect Python executable
set "PYTHON_EXE=C:\Users\Manudev Sharma\AppData\Local\Programs\Python\Python311\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

set "PYTHONIOENCODING=utf-8"

echo [1/3] Starting QuantScreener Agent on port 8002...
start "FinPilot - QuantScreener Agent (Port 8002)" cmd /k "chcp 65001 >nul && "%PYTHON_EXE%" finpilot/screener.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting DeepResearcher Agent on port 8004...
start "FinPilot - DeepResearcher Agent (Port 8004)" cmd /k "chcp 65001 >nul && "%PYTHON_EXE%" finpilot/researcher.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Orchestrator Agent (ASI:One ACP Mailbox) on port 8000...
start "FinPilot - Orchestrator Agent (Port 8000)" cmd /k "chcp 65001 >nul && "%PYTHON_EXE%" finpilot/orchestrator.py"

echo.
echo ============================================================================
echo All 3 Fetch.ai agents have been launched in separate terminal windows!
echo.
echo - Orchestrator Agent : agent1qg9wlw06ulhcjcwvfghyrtkdyzcfngaf4jsysdtughqfu8swlp9ryrk2vzm
echo - QuantScreener Agent: agent1qgrmhgl5z5exyd7wre4v0t38lu64hcwwqde56eym9x55w7pk6whzcu3karf
echo - DeepResearcher Agent: agent1qtzv0v7hcpc7dvk23e7ugzsh29edr7v07r5elflddjj5e8axq6f6zn0d3d4
echo.
echo Connected to Agentverse Mailbox Relay for 24/7 ASI:One message routing!
echo To test locally without ASI:One, open a new terminal and run:
echo   python finpilot/trigger.py
echo ============================================================================
pause
