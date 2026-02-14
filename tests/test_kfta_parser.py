import unittest
from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kfta_excel.kfta_parser import KFTAParser


class KFTAParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = KFTAParser()

    def test_school_abbreviation_expansion(self):
        self.assertEqual(self.parser.expand_school_abbreviation("춘천공고"), "춘천공업고등학교")
        self.assertEqual(self.parser.expand_school_abbreviation("속초여고"), "속초여자고등학교")

    def test_abbreviated_school_format(self):
        office, school = self.parser.parse_abbreviated_school_format("춘천 남산초")
        self.assertEqual(office, "강원특별자치도춘천교육지원청")
        self.assertEqual(school, "남산초등학교")

    def test_position_normalization(self):
        self.assertEqual(self.parser.normalize_position("초등학교 교감"), "교감")
        self.assertEqual(self.parser.normalize_position("특수학교 교사(중등)"), "특수교사")


if __name__ == "__main__":
    unittest.main()
