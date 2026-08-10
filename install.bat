@echo off
setlocal
title CSQAQ MCP Server - Installer

echo ==================================================
echo   CSQAQ MCP Server - One-click Installer
echo ==================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo Please install Python 3.12+ from https://www.python.org/downloads/
    echo and make sure "Add Python to PATH" is checked during install.
    pause
    exit /b 1
)

echo [1/2] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/2] Installing dependencies: mcp + requests...
call ".venv\Scripts\activate.bat"
pip install --quiet mcp==1.29.0 requests
if errorlevel 1 (
    echo [ERROR] pip install failed. Check your network and retry.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo   Installation complete!
echo ==================================================
echo.
echo   NEXT STEP - configure your API token:
echo     1. Copy ".env.example" to ".env"
echo     2. Open ".env" and replace YOUR_TOKEN_HERE
echo        with your CSQAQ API token
echo     3. Make sure your IP is whitelisted on CSQAQ
echo.
echo   Start the server with:
echo       .venv\Scripts\python.exe server.py
echo.
pause
