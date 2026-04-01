@echo off
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║       Tesqo — First-Time Setup             ║
echo  ║   Automate your web tests with ease        ║
echo  ╚══════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM Create virtual environment
echo  [1/5] Creating virtual environment...
if not exist .venv (python -m venv .venv)
if errorlevel 1 (echo  ERROR: Python not found. Install Python 3.11+ first. & pause & exit /b 1)

REM Activate and install deps
echo  [2/5] Installing dependencies...
call .venv\Scripts\activate
pip install -r requirements.txt --quiet

REM Install browsers
echo  [3/5] Installing Playwright browsers (Chromium + Edge)...
python -m playwright install chromium msedge

REM Copy .env if not exists
echo  [4/5] Setting up .env file...
if not exist .env (
    copy .env.example .env >nul
    echo         .env created from .env.example — open it and set your BASE_URL, USERNAME, PASSWORD
) else (
    echo         .env already exists — skipping
)

REM Create sample Excel data
echo  [5/5] Creating sample test_data.xlsx...
python data\create_sample_data.py

echo.
echo  ✅  Setup complete!
echo.
echo  Next steps:
echo    1. Edit .env  — set BASE_URL, USERNAME, PASSWORD
echo    2. record.bat — record your first test
echo    3. run.bat    — run tests interactively
echo.
pause
