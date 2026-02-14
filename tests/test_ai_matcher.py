import os
import unittest
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kfta_excel.ai_matcher import GeminiMatcher


class GeminiMatcherConfigTest(unittest.TestCase):
    def test_model_candidates_default_priority(self):
        original = os.environ.get("GEMINI_MODEL")
        try:
            os.environ.pop("GEMINI_MODEL", None)
            candidates = GeminiMatcher._build_model_candidates(None, None)
            self.assertGreaterEqual(len(candidates), 3)
            self.assertEqual(candidates[0], "gemini-3-flash")
            self.assertIn("gemini-2.5-flash", candidates)
        finally:
            if original is None:
                os.environ.pop("GEMINI_MODEL", None)
            else:
                os.environ["GEMINI_MODEL"] = original

    def test_model_candidates_honor_explicit_primary(self):
        candidates = GeminiMatcher._build_model_candidates(
            "gemini-3-flash",
            ["gemini-2.5-flash", "gemini-2.5-flash"],
        )
        self.assertEqual(candidates[0], "gemini-3-flash")
        self.assertEqual(candidates.count("gemini-2.5-flash"), 1)

    def test_model_candidates_honor_env_when_no_explicit(self):
        original = os.environ.get("GEMINI_MODEL")
        try:
            os.environ["GEMINI_MODEL"] = "gemini-3-flash"
            candidates = GeminiMatcher._build_model_candidates(None, None)
            self.assertEqual(candidates[0], "gemini-3-flash")
        finally:
            if original is None:
                os.environ.pop("GEMINI_MODEL", None)
            else:
                os.environ["GEMINI_MODEL"] = original


if __name__ == "__main__":
    unittest.main()
