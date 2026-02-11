@echo off
chcp 65001 > nul
title AI-Votes

echo ==============================================
echo   AI-Votes System Launcher
echo ==============================================
echo.

cd /d "%~dp0"

:: Check Python
echo [Step 1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python 3.10+
    goto :error
)
python --version
echo.

:: Check venv
echo [Step 2/5] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo Found venv, activating...
    call venv\Scripts\activate.bat
    echo Activated
) else (
    echo Using system Python
    echo Tip: python -m venv venv
)
echo.

:: Check dependencies
echo [Step 3/5] Checking dependencies...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Installation failed
        goto :error
    )
    echo Installed
) else (
    echo OK
)
echo.

:: Initialize database
echo [Step 4/5] Initializing database...
if not exist "data" mkdir data
echo OK
echo.

:: Start server
echo [Step 5/5] Starting server...
echo ==============================================
echo.
echo Access URLs:
echo   Display: http://localhost:8000/
echo   Admin:   http://localhost:8000/admin
echo   Sign-in: http://localhost:8000/signin
echo   Host:    http://localhost:8000/host
echo.
echo Default passwords:
echo   Admin: admin123
echo   Host:  host123
echo.
echo ==============================================
echo Press Ctrl+C to stop
echo ==============================================
echo.

python -m backend.main

if errorlevel 1 (
    echo.
    echo ERROR: Server failed
    goto :error
)

echo.
echo Server stopped
pause
exit /b 0

:error
echo.
echo ==============================================
echo ERROR: Launch failed
echo ==============================================
echo.
echo Troubleshooting:
echo   1. Port in use - Edit .env PORT
echo   2. Missing deps - pip install -r requirements.txt
echo   3. Python 3.10+ required
echo.
pause
exit /b 1