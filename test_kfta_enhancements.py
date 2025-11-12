#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KFTA Parser 개선사항 테스트
"""

from kfta_parser import KFTAParser
import pandas as pd


def test_school_abbreviation_expansion():
    """학교 약칭 확장 테스트"""
    print("=" * 70)
    print("테스트 1: 학교 약칭 확장")
    print("=" * 70)

    parser = KFTAParser()

    test_cases = [
        ("춘천공고", "춘천공업고등학교"),
        ("원주정산고", "원주정보산업고등학교"),
        ("강릉산과고", "강릉산업과학고등학교"),
        ("속초여고", "속초여자고등학교"),
        ("삼척여중", "삼척여자중학교"),
        ("태백고", "태백고등학교"),
        ("영월중", "영월중학교"),
        ("평창초", "평창초등학교"),
    ]

    for input_name, expected in test_cases:
        result = parser.expand_school_abbreviation(input_name)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_name}' → '{result}' (기대값: '{expected}')")


def test_abbreviated_school_format():
    """약식 학교명 파싱 테스트"""
    print("\n" + "=" * 70)
    print("테스트 2: 약식 학교명 파싱 (□□ OO초 형식)")
    print("=" * 70)

    parser = KFTAParser()

    test_cases = [
        ("춘천 남산초", "강원특별자치도춘천교육지원청", "남산초등학교"),
        ("원주중앙초", "강원특별자치도원주교육지원청", "중앙초등학교"),
        ("강릉 명주초", "강원특별자치도강릉교육지원청", "명주초등학교"),
        ("홍천 내촌초", "강원특별자치도홍천교육지원청", "내촌초등학교"),
    ]

    for input_name, expected_office, expected_school in test_cases:
        office, school = parser.parse_abbreviated_school_format(input_name)
        status = "✓" if (office == expected_office and school == expected_school) else "✗"
        print(f"  {status} '{input_name}'")
        print(f"      교육청: '{office}' (기대값: '{expected_office}')")
        print(f"      학교명: '{school}' (기대값: '{expected_school}')")


def test_position_normalization():
    """직위명 정규화 테스트"""
    print("\n" + "=" * 70)
    print("테스트 3: 직위명 정규화")
    print("=" * 70)

    parser = KFTAParser()

    test_cases = [
        ("초등학교 교감", "교감"),
        ("중등학교 교감", "교감"),
        ("초등학교교감", "교감"),
        ("중등학교교감", "교감"),
        ("초등학교 교사", "교사"),
        ("중등학교 교사", "교사"),
        ("초등학교교사", "교사"),
        ("중등학교교사", "교사"),
        ("특수학교교사(초등)", "특수교사"),
        ("특수학교교사(중등)", "특수교사"),
        ("특수학교 교사(초등)", "특수교사"),
        ("특수학교 교사(중등)", "특수교사"),
        ("특수학교교사", "특수교사"),
    ]

    for input_pos, expected in test_cases:
        result = parser.normalize_position(input_pos)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_pos}' → '{result}' (기대값: '{expected}')")


def test_row_parsing():
    """행 파싱 통합 테스트"""
    print("\n" + "=" * 70)
    print("테스트 4: 행 데이터 파싱 통합")
    print("=" * 70)

    parser = KFTAParser()

    # 테스트 데이터: 인덱스 기반 (0부터 시작)
    # 2: 대응, 4: 직위, 5: 발령본청
    test_data = {
        0: ['', '', '홍길동', '', '초등학교 교사', '춘천 남산초', '', '', '', ''],
        1: ['', '', '김철수', '', '중등학교 교감', '원주공고', '', '강릉산과고', '', ''],
    }

    for idx, row_data in test_data.items():
        row = pd.Series(row_data)
        result = parser.parse_row_to_kfta(row)

        print(f"\n  행 {idx}:")
        print(f"    대응: {result['대응']}")
        print(f"    직위: {result['직위']}")
        print(f"    발령교육청: {result['발령교육청']}")
        print(f"    발령본청: {result['발령본청']}")
        print(f"    현재교육청: {result['현재교육청']}")
        print(f"    현재본청: {result['현재본청']}")


if __name__ == '__main__':
    print("\n🧪 KFTA Parser 개선사항 테스트 시작\n")

    test_school_abbreviation_expansion()
    test_abbreviated_school_format()
    test_position_normalization()
    test_row_parsing()

    print("\n" + "=" * 70)
    print("✅ 모든 테스트 완료")
    print("=" * 70)
