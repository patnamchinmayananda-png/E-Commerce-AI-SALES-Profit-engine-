#!/usr/bin/env bash

# ==============================================================================
# E-Commerce AI Sales & Profit Engine - One-Click Launcher
# ==============================================================================

set -e

PORT=8088

# Kill any existing process on port 8088 to avoid address conflict
lsof -ti :${PORT} | xargs kill -9 2>/dev/null || true

echo "=================================================================="
echo "🤖 E-Commerce AI Sales & Profit Engine (FY 2018)"
echo "=================================================================="
echo "1. Running Python analytical validation engine..."
python3 analysis.py

echo ""
echo "2. Launching interactive web application on port ${PORT}..."

# Open in default browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    (sleep 1 && open "http://localhost:${PORT}") &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    (sleep 1 && xdg-open "http://localhost:${PORT}") &
fi

echo "=================================================================="
echo "🚀 Dashboard live at: http://localhost:${PORT}"
echo "Press Ctrl+C to stop the local server."
echo "=================================================================="

python3 -m http.server ${PORT}
