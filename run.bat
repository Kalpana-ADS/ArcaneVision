@echo off
echo ================================================
echo   ArcaneVision - AI Magical Hand Gesture System
echo ================================================
cd /d %~dp0
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo Starting ArcaneVision...
python -m src.main
pause
