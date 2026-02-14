#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backward-compatible entrypoint for ExcelUnifier."""

from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from kfta_excel.excel_unifier import ExcelUnifier, main

__all__ = ["ExcelUnifier", "main"]

if __name__ == '__main__':
    main()
