#!/usr/bin/env bash
set -e

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}Google SEO APIs — Setup${RESET}"
echo "──────────────────────────────────────────"

# 1. Check Python 3.8+
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}Error: Python 3 not found.${RESET}"
  echo "Download Python 3.8+ from: https://www.python.org/downloads/"
  exit 1
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo "$PYTHON_VER" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VER" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]; }; then
  echo -e "${RED}Error: Python 3.8+ required (found $PYTHON_VER).${RESET}"
  echo "Download from: https://www.python.org/downloads/"
  exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VER found${RESET}"

# 2. Create virtual environment
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_DIR/venv"

if [ -d "$VENV_DIR" ]; then
  echo "  Existing venv found — skipping creation"
else
  echo "  Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
  echo -e "${GREEN}✓ Virtual environment created${RESET}"
fi

# 3. Install dependencies
echo "  Installing dependencies (this may take a minute)..."
"$VENV_DIR/bin/pip" install -r "$REPO_DIR/requirements.txt" -q --disable-pip-version-check
echo -e "${GREEN}✓ Dependencies installed${RESET}"

# 4. Check credentials
echo ""
echo "Checking credentials..."
"$VENV_DIR/bin/python" "$REPO_DIR/scripts/auth.py" --check

echo ""
echo "One more step: authenticate with Google Search Console."
echo "Run:  source venv/bin/activate && python scripts/auth.py --auth --creds /path/to/client_secret.json"
echo "See docs/03-credentials.md for how to get your client_secret.json file."

# 5. Next steps
echo ""
echo -e "${BOLD}Setup complete!${RESET}"
echo ""
echo "To run PageSpeed Insights:"
echo -e "  ${YELLOW}source venv/bin/activate${RESET}"
echo -e "  ${YELLOW}python scripts/psi.py https://example.com${RESET}"
echo ""
echo "To run Search Console:"
echo -e "  ${YELLOW}python scripts/gsc.py --property sc-domain:example.com${RESET}"
echo ""
echo "Need credentials? See docs/03-credentials.md"
