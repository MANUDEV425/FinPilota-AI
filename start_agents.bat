@echo off
REM ============================================================================
REM FinPilot AI - Fetch.ai Multi-Agent Launch Script (ASI:One / Hackathon)
REM ============================================================================

echo ============================================================================
echo Starting FinPilot AI Fetch.ai Agent Network...
echo ============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting QuantScreener Agent on port 8002...
start "FinPilot - QuantScreener Agent" cmd /k "python finpilot/screener.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting DeepResearcher Agent on port 8004...
start "FinPilot - DeepResearcher Agent" cmd /k "python finpilot/researcher.py"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Orchestrator Agent (ASI:One ACP) on port 8000...
start "FinPilot - Orchestrator Agent" cmd /k "python finpilot/orchestrator.py"

echo.
echo ============================================================================
echo All 3 Fetch.ai agents are running!
echo - Orchestrator: agent1qg9wlw06ulhcjcwvfghyrtkdyzcfngaf4jsysdtughqfu8swlp9ryrk2vzm (Port 8000)
echo - QuantScreener: agent1qgrmhgl5z5exyd7wre4v0t38lu64hcwwqde56eym9x55w7pk6whzcu3karf (Port 8002)
echo - DeepResearcher: agent1qtzv0v7hcpc7dvk23e7ugzsh29edr7v07r5elflddjj5e8axq6f6zn0d3d4 (Port 8004)
echo.
echo You can test the agent network locally by running:
echo   python finpilot/trigger.py
echo ============================================================================
pause
