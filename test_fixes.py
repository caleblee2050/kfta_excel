#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 피드백 기반 수정사항 테스트
"""

from kfta_parser import KFTAParser
import pandas as pd


def test_specific_school_mappings():
    """특정 학교 매핑 테스트"""
    print("=" * 70)
    print("테스트 1: 특정 학교 매핑 데이터베이스")
    print("=" * 70)

    parser = KFTAParser()

    test_cases = [
        # (입력, 기대 교육청, 기대 학교명)
        ("동산중학교", "강원특별자치도춘천교육지원청", "동산중학교"),
        ("동광산과고", "강원특별자치도원주교육지원청", "동광산업과학고등학교"),
        ("동광산업과학고등학교", "강원특별자치도원주교육지원청", "동광산업과학고등학교"),
        ("강원생명과학고등학교", "강원특별자치도원주교육지원청", "강원생명과학고등학교"),
    ]

    for input_name, expected_office, expected_school in test_cases:
        office, school = parser.parse_abbreviated_school_format(input_name)
        status = "✓" if (office == expected_office and school == expected_school) else "✗"
        print(f"\n  {status} '{input_name}'")
        print(f"      교육청: {office}")
        print(f"      (기대): {expected_office}")
        print(f"      학교명: {school}")
        print(f"      (기대): {expected_school}")


def test_region_prefix_preservation():
    """지역명으로 시작하는 학교명 보존 테스트"""
    print("\n" + "=" * 70)
    print("테스트 2: 지역명으로 시작하는 학교명 (춘천교대부설초, 춘천중 등)")
    print("=" * 70)

    parser = KFTAParser()

    test_cases = [
        # (입력, 기대 학교명) - 교육청은 빈 문자열이어야 함 (지역명이 학교명의 일부)
        ("춘천교대부설초등학교", "춘천교대부설초등학교"),
        ("춘천중학교", "춘천중학교"),
        ("춘천고등학교", "춘천고등학교"),
        ("춘천기계공업고등학교", "춘천기계공업고등학교"),
        # 공백이 있는 경우는 지역명 제거되어야 함
        ("춘천 남산초", "남산초등학교"),
        ("원주 중앙초", "중앙초등학교"),
    ]

    for input_name, expected_school in test_cases:
        office, school = parser.parse_abbreviated_school_format(input_name)
        status = "✓" if school == expected_school else "✗"
        print(f"\n  {status} '{input_name}' → '{school}'")
        print(f"      (기대): '{expected_school}'")
        if office:
            print(f"      교육청: {office}")


def test_other_region_detection():
    """타시도 학교 감지 테스트"""
    print("\n" + "=" * 70)
    print("테스트 3: 타시도 학교 감지")
    print("=" * 70)

    parser = KFTAParser()

    test_cases = [
        # (입력, 기대 교육청, 기대 학교명)
        ("서울 성원초등학교", "", "성원초등학교"),  # 교육청 빈 문자열
        ("경기 수원초등학교", "", "수원초등학교"),
        ("부산 해운초등학교", "", "해운초등학교"),
    ]

    for input_name, expected_office, expected_school in test_cases:
        office, school = parser.parse_abbreviated_school_format(input_name)
        status = "✓" if (office == expected_office and school == expected_school) else "✗"
        print(f"\n  {status} '{input_name}'")
        print(f"      교육청: '{office}' (기대: '{expected_office}')")
        print(f"      학교명: '{school}' (기대: '{expected_school}')")


def test_clean_school_name():
    """학교명 정리 테스트 (전문상담 등 제거)"""
    print("\n" + "=" * 70)
    print("테스트 4: 학교명에서 불필요한 텍스트 제거")
    print("=" * 70)

    parser = KFTAParser()

    test_cases = [
        ("동광산과고 전문상담", "동광산과고"),
        ("춘천교대부설초등학교 보건", "춘천교대부설초등학교"),
        ("동산중학교 영양", "동산중학교"),
        ("남산초등학교", "남산초등학교"),  # 변화 없음
    ]

    for input_name, expected in test_cases:
        result = parser.clean_school_name(input_name)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_name}' → '{result}' (기대: '{expected}')")


if __name__ == '__main__':
    print("\n🧪 사용자 피드백 기반 수정사항 테스트\n")

    test_specific_school_mappings()
    test_region_prefix_preservation()
    test_other_region_detection()
    test_clean_school_name()

    print("\n" + "=" * 70)
    print("✅ 모든 테스트 완료")
    print("=" * 70)
