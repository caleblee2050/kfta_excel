#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backward-compatible import path for GeminiMatcher."""

from pathlib import Path
import sys

SRC_PATH = Path(__file__).resolve().parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from kfta_excel.ai_matcher import GeminiMatcher

__all__ = ["GeminiMatcher"]
