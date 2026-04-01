#!/usr/bin/env bash
# setup.sh — Tesqo first-time setup for macOS / Linux

set -e

echo ""
echo " ╔══════════════════════════════════════════════════╗"
echo " ║       Tesqo — First-Time Setup                   ║"
echo " ║   Automate your web tests with ease              ║"
echo " ╚══════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# ── 1 / 5  Virtual environment ────────────────────────────────────────
echo " [1/5] Creating virtual environment..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv || { echo " ERROR: python3 not found. Install Python 3.11+ first."; exit 1; }
fi

# ── 2 / 5  Activate and install dependencies ─────────────────────────
echo " [2/5] Installing dependencies..."
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt --quiet

# ── 3 / 5  Playwright browsers ────────────────────────────────────────
echo " [3/5] Installing Playwright browsers (Chromium + Edge)..."
python -m playwright install chromium msedge

# ── 4 / 5  .env ───────────────────────────────────────────────────────
echo " [4/5] Setting up .env file..."
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "        .env created from .env.example — open it and set BASE_URL, USERNAME, PASSWORD"
else
  echo "        .env already exists — skipping"
fi

# ── 5 / 5  Sample Excel data ──────────────────────────────────────────
echo " [5/5] Creating sample test_data.xlsx..."
python data/create_sample_data.py

echo ""
echo " ✅  Setup complete!"
echo ""
echo " Next steps:"
echo "   1. Edit .env       — set BASE_URL, USERNAME, PASSWORD"
echo "   2. make record     — record your first test"
echo "   3. make run        — run tests interactively"
echo "   4. make smoke      — run smoke tests directly"
echo ""
