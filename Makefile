# Makefile — Tesqo universal commands (macOS · Linux · Windows Git Bash / WSL)
# Usage:  make <target>
# Windows cmd.exe users: use setup.bat / run.bat / record.bat directly.

.PHONY: help setup install browsers record run smoke regression automation \
        report clean lint check

# ── Detect OS & venv python ───────────────────────────────────────────
ifeq ($(OS),Windows_NT)
  PYTHON  := .venv\Scripts\python.exe
  PIP     := .venv\Scripts\pip.exe
  ACTIVATE := .venv\Scripts\activate
else
  PYTHON  := .venv/bin/python
  PIP     := .venv/bin/pip
  ACTIVATE := .venv/bin/activate
endif

# ── Default target ────────────────────────────────────────────────────
help:
	@echo ""
	@echo " Tesqo — Available make targets"
	@echo " ─────────────────────────────────────────────"
	@echo "  make setup        First-time setup (venv + deps + browsers)"
	@echo "  make install      Install / refresh Python dependencies"
	@echo "  make browsers     Install / update Playwright browsers"
	@echo "  make record       Launch the interactive test recorder"
	@echo "  make run          Launch the interactive test runner menu"
	@echo "  make smoke        Run @pytest.mark.smoke tests"
	@echo "  make regression   Run @pytest.mark.regression tests"
	@echo "  make automation   Run @pytest.mark.automation scripts"
	@echo "  make all-tests    Run the full test suite"
	@echo "  make report       Open the last HTML report"
	@echo "  make clean        Remove __pycache__, .pytest_cache, temp reports"
	@echo "  make check        Verify the Python environment is ready"
	@echo " ─────────────────────────────────────────────"
	@echo ""

# ── Setup ─────────────────────────────────────────────────────────────
setup:
ifeq ($(OS),Windows_NT)
	@echo "[setup] Running setup.bat..."
	@setup.bat
else
	@echo "[setup] Running setup.sh..."
	@chmod +x setup.sh && bash setup.sh
endif

# ── Install dependencies ──────────────────────────────────────────────
install:
	@echo "[install] Creating venv if missing..."
ifeq ($(OS),Windows_NT)
	@if not exist .venv (python -m venv .venv)
else
	@test -d .venv || python3 -m venv .venv
endif
	$(PIP) install -r requirements.txt

# ── Playwright browsers ───────────────────────────────────────────────
browsers:
	$(PYTHON) -m playwright install chromium msedge

# ── Recorder ─────────────────────────────────────────────────────────
record:
	$(PYTHON) scripts/record.py

# ── Interactive runner ────────────────────────────────────────────────
run:
	$(PYTHON) scripts/run.py

# ── Direct test targets ───────────────────────────────────────────────
smoke:
	$(PYTHON) -m pytest tests/ -m smoke -v \
		--html=reports/html/report.html --self-contained-html

regression:
	$(PYTHON) -m pytest tests/ -m regression -v \
		--html=reports/html/report.html --self-contained-html

automation:
	$(PYTHON) -m pytest tests/ -m automation -v \
		--html=reports/html/report.html --self-contained-html

all-tests:
	$(PYTHON) -m pytest tests/ -v \
		--html=reports/html/report.html --self-contained-html

# ── Report ────────────────────────────────────────────────────────────
report:
ifeq ($(OS),Windows_NT)
	@start reports\html\report.html
else ifeq ($(shell uname),Darwin)
	@open reports/html/report.html
else
	@xdg-open reports/html/report.html
endif

# ── Clean ─────────────────────────────────────────────────────────────
clean:
ifeq ($(OS),Windows_NT)
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
	@if exist .pytest_cache rd /s /q .pytest_cache
else
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache
endif
	@echo "[clean] Done."

# ── Check environment ─────────────────────────────────────────────────
check:
	@echo "[check] Python version:"
	@$(PYTHON) --version
	@echo "[check] Installed packages:"
	@$(PIP) list --format=columns | grep -E "playwright|pytest|openpyxl|dotenv" || true
	@echo "[check] Playwright browsers:"
	@$(PYTHON) -m playwright --version
