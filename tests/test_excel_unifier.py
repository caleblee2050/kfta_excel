import unittest
from pathlib import Path
import tempfile
import sys

import pandas as pd

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kfta_excel.excel_unifier import ExcelUnifier


class ExcelUnifierTest(unittest.TestCase):
    def test_analyze_columns_keyword_mapping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first = base / "a.csv"
            second = base / "b.csv"

            pd.DataFrame(
                {
                    "이름": ["김철수"],
                    "학교": ["서울대학교"],
                    "전공": ["컴퓨터공학"],
                }
            ).to_csv(first, index=False)

            pd.DataFrame(
                {
                    "성명": ["김철수"],
                    "대학교": ["서울대"],
                    "전공분야": ["컴퓨터공학"],
                }
            ).to_csv(second, index=False)

            unifier = ExcelUnifier(similarity_threshold=80)
            unifier.load_excel_files([str(first), str(second)])
            mappings = unifier.analyze_columns()

            self.assertIn("이름", mappings)
            self.assertIn("성명", mappings["이름"])
            self.assertIn("학교", mappings)
            self.assertIn("대학교", mappings["학교"])

    def test_unify_dataframes_dedup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first = base / "a.csv"
            second = base / "b.csv"

            pd.DataFrame(
                {
                    "이름": ["김철수", "이영희"],
                    "학교": ["서울대학교", "연세대학교"],
                    "전공": ["컴퓨터공학", "경영학"],
                }
            ).to_csv(first, index=False)

            pd.DataFrame(
                {
                    "성명": ["김철수", "박민수"],
                    "대학교": ["서울대", "고려대학교"],
                    "전공": ["컴퓨터공학", "전자공학"],
                }
            ).to_csv(second, index=False)

            unifier = ExcelUnifier(similarity_threshold=80)
            unifier.load_excel_files([str(first), str(second)])
            unifier.analyze_columns()
            unified = unifier.unify_dataframes(key_columns=["이름", "학교"])

            self.assertEqual(len(unified), 3)
            self.assertTrue({"이름", "현재분회", "과목"}.issubset(set(unified.columns)))
            # 일반 컬럼(학교/전공)이 KFTA 컬럼으로 보강되는지 확인
            self.assertIn("서울대학교", set(unified["현재분회"].tolist()))
            self.assertIn("컴퓨터공학", set(unified["과목"].tolist()))

    def test_kfta_output_for_non_kfta_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            first = base / "a.csv"
            second = base / "b.csv"

            pd.DataFrame(
                {
                    "이름": ["김철수", "이영희"],
                    "학교": ["서울대학교", "연세대학교"],
                    "전공": ["컴퓨터공학", "경영학"],
                }
            ).to_csv(first, index=False)

            pd.DataFrame(
                {
                    "성명": ["박민수"],
                    "대학교": ["고려대학교"],
                    "전공분야": ["전자공학"],
                }
            ).to_csv(second, index=False)

            unifier = ExcelUnifier(similarity_threshold=80)
            unifier.load_excel_files([str(first), str(second)])
            unifier.analyze_columns()
            unified = unifier.unify_dataframes(
                key_columns=["이름", "현재분회"],
                output_format="kfta",
            )

            self.assertEqual(len(unified), 3)
            self.assertEqual(set(unified["이름"].tolist()), {"김철수", "이영희", "박민수"})
            self.assertIn("서울대학교", set(unified["현재분회"].tolist()))
            self.assertIn("전자공학", set(unified["과목"].tolist()))


if __name__ == "__main__":
    unittest.main()
