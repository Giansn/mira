#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT_DIR/venv"

if [ -d "$VENV" ]; then
  echo "Virtualenv already exists at $VENV"
else
  python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"
pip install --upgrade pip >/dev/null 2>&1 || true
echo "Environment ready. Activate with: source $VENV/bin/activate"
