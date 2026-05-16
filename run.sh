#!/usr/bin/env bash
echo "================================================"
echo "  ArcaneVision - AI Magical Hand Gesture System"
echo "================================================"
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "Starting ArcaneVision..."
python -m src.main
