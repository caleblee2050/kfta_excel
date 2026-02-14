#!/bin/bash
set -euo pipefail

if [ -d "venv" ]; then
  PYTHON="venv/bin/python"
else
  PYTHON="python3"
fi

"$PYTHON" scripts/verify.py
