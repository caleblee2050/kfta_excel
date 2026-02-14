# Verification Process

## Quick Run

```bash
./scripts/verify.sh
```

## What It Checks

1. Syntax/Import compilation check for `src`, `tests`, `scripts`
2. Automated unit tests in `tests/test_*.py`

## Local UI Smoke (Optional)

1. Run app:

```bash
venv/bin/python -m streamlit run app.py --server.headless true --server.port 8765
```

2. Run Playwright/browser smoke:
- Upload sample files in `examples/`
- Execute 통합 버튼
- Validate metrics + result table + download button rendering

## CI-friendly command

```bash
python3 scripts/verify.py
```
