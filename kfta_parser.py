#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KFTA Excel Parser - 강원교총 전용 엑셀 파서
특정 필드 위치 기반으로 데이터 추출 및 변환
"""

import pandas as pd
import re
from typing import Dict, List, Optional


class KFTAParser:
    """강원교총 엑셀 파일 파서"""

    # 강원도 지역명과 교육청 매핑
    GANGWON_REGIONS = {
        '춘천': '강원특별자치도춘천교육지원청',
        '원주': '강원특별자치도원주교육지원청',
        '강릉': '강원특별자치도강릉교육지원청',
        '동해': '강원특별자치도동해교육지원청',
        '태백': '강원특별자치도태백교육지원청',
        '속초': '강원특별자치도속초양양교육지원청',
        '양양': '강원특별자치도속초양양교육지원청',
        '삼척': '강원특별자치도삼척교육지원청',
        '홍천': '강원특별자치도홍천교육지원청',
        '횡성': '강원특별자치도횡성교육지원청',
        '영월': '강원특별자치도영월교육지원청',
        '평창': '강원특별자치도평창교육지원청',
        '정선': '강원특별자치도정선교육지원청',
        '철원': '강원특별자치도철원교육지원청',
        '화천': '강원특별자치도화천교육지원청',
        '양구': '강원특별자치도양구교육지원청',
        '인제': '강원특별자치도인제교육지원청',
        '고성': '강원특별자치도고성교육지원청',
    }

    # 강원도 중고등학교와 교육지원청 매핑
    # 학교명 키워드 → 교육지원청
    MIDDLE_HIGH_SCHOOL_REGION_MAP = {
        # 춘천
        '춘천': '강원특별자치도춘천교육지원청',
        # 원주
        '원주': '강원특별자치도원주교육지원청',
        # 강릉
        '강릉': '강원특별자치도강릉교육지원청',
        '경포': '강원특별자치도강릉교육지원청',
        '명륜': '강원특별자치도강릉교육지원청',
        '옥계': '강원특별자치도강릉교육지원청',
        # 동해
        '동해': '강원특별자치도동해교육지원청',
        '묵호': '강원특별자치도동해교육지원청',
        '북평': '강원특별자치도동해교육지원청',
        '하랑': '강원특별자치도동해교육지원청',
        '예람': '강원특별자치도동해교육지원청',
        # 태백
        '태백': '강원특별자치도태백교육지원청',
        # 속초/양양
        '속초': '강원특별자치도속초양양교육지원청',
        '양양': '강원특별자치도속초양양교육지원청',
        # 삼척
        '삼척': '강원특별자치도삼척교육지원청',
        '근덕': '강원특별자치도삼척교육지원청',
        '도계': '강원특별자치도삼척교육지원청',
        # 홍천
        '홍천': '강원특별자치도홍천교육지원청',
        # 횡성
        '횡성': '강원특별자치도횡성교육지원청',
        '우천': '강원특별자치도횡성교육지원청',
        # 영월
        '영월': '강원특별자치도영월교육지원청',
        # 평창
        '평창': '강원특별자치도평창교육지원청',
        '진부': '강원특별자치도평창교육지원청',
        # 정선
        '정선': '강원특별자치도정선교육지원청',
        '사북': '강원특별자치도정선교육지원청',
        # 철원
        '철원': '강원특별자치도철원교육지원청',
        # 화천
        '화천': '강원특별자치도화천교육지원청',
        # 양구
        '양구': '강원특별자치도양구교육지원청',
        # 인제
        '인제': '강원특별자치도인제교육지원청',
        # 고성
        '고성': '강원특별자치도고성교육지원청',
        # 기타 유명 중고등학교
        '하슬라': '강원특별자치도강릉교육지원청',
        '청아': '강원특별자치도춘천교육지원청',
        '제일': '강원특별자치도강릉교육지원청',
    }

    # 강원도 학교 데이터베이스 (중복 학교명 포함)
    # 형식: {학교명: {교육청: 정식학교명}}
    GANGWON_SCHOOL_DATABASE = {
        # 중복 학교명 - 원당초등학교
        '원당초등학교': {
            '강원특별자치도홍천교육지원청': '홍천원당초등학교',
            '강원특별자치도양구교육지원청': '양구원당초등학교',
        },
        '원당초': {
            '강원특별자치도홍천교육지원청': '홍천원당초등학교',
            '강원특별자치도양구교육지원청': '양구원당초등학교',
        },
        # 중복 학교명 - 신동초등학교
        '신동초등학교': {
            '강원특별자치도춘천교육지원청': '춘천신동초등학교',
            '강원특별자치도삼척교육지원청': '삼척신동초등학교',
        },
        '신동초': {
            '강원특별자치도춘천교육지원청': '춘천신동초등학교',
            '강원특별자치도삼척교육지원청': '삼척신동초등학교',
        },
        # 중복 학교명 - 반곡초등학교
        '반곡초등학교': {
            '강원특별자치도원주교육지원청': '원주반곡초등학교',
            '강원특별자치도홍천교육지원청': '홍천반곡초등학교',
        },
        '반곡초': {
            '강원특별자치도원주교육지원청': '원주반곡초등학교',
            '강원특별자치도홍천교육지원청': '홍천반곡초등학교',
        },
        # 중복 학교명 - 교동초등학교
        '교동초등학교': {
            '강원특별자치도춘천교육지원청': '춘천교동초등학교',
            '강원특별자치도원주교육지원청': '원주교동초등학교',
            '강원특별자치도강릉교육지원청': '강릉교동초등학교',
            '강원특별자치도속초양양교육지원청': '속초교동초등학교',
        },
        '교동초': {
            '강원특별자치도춘천교육지원청': '춘천교동초등학교',
            '강원특별자치도원주교육지원청': '원주교동초등학교',
            '강원특별자치도강릉교육지원청': '강릉교동초등학교',
            '강원특별자치도속초양양교육지원청': '속초교동초등학교',
        },
        # 중복 학교명 - 속초초등학교
        '속초초등학교': {
            '강원특별자치도속초양양교육지원청': '속초초등학교',  # 속초는 그대로
            '강원특별자치도홍천교육지원청': '홍천속초초등학교',
        },
        '속초초': {
            '강원특별자치도속초양양교육지원청': '속초초등학교',
            '강원특별자치도홍천교육지원청': '홍천속초초등학교',
        },
        # 중복 학교명 - 중앙초등학교
        '중앙초등학교': {
            '강원특별자치도춘천교육지원청': '춘천중앙초등학교',
            '강원특별자치도원주교육지원청': '원주중앙초등학교',
            '강원특별자치도강릉교육지원청': '강릉중앙초등학교',
            '강원특별자치도속초양양교육지원청': '속초중앙초등학교',
            '강원특별자치도삼척교육지원청': '삼척중앙초등학교',
            '강원특별자치도동해교육지원청': '동해중앙초등학교',  # 동해중앙초는 기본 학교명
        },
        '중앙초': {
            '강원특별자치도춘천교육지원청': '춘천중앙초등학교',
            '강원특별자치도원주교육지원청': '원주중앙초등학교',
            '강원특별자치도강릉교육지원청': '강릉중앙초등학교',
            '강원특별자치도속초양양교육지원청': '속초중앙초등학교',
            '강원특별자치도삼척교육지원청': '삼척중앙초등학교',
            '강원특별자치도동해교육지원청': '동해중앙초등학교',
        },
        # 중복 학교명 - 조양초등학교
        '조양초등학교': {
            '강원특별자치도춘천교육지원청': '춘천조양초등학교',
            '강원특별자치도속초양양교육지원청': '속초조양초등학교',
        },
        '조양초': {
            '강원특별자치도춘천교육지원청': '춘천조양초등학교',
            '강원특별자치도속초양양교육지원청': '속초조양초등학교',
        },
        # 중복 학교명 - 남산초등학교
        '남산초등학교': {
            '강원특별자치도춘천교육지원청': '춘천남산초등학교',
            '강원특별자치도강릉교육지원청': '강릉남산초등학교',
            '강원특별자치도홍천교육지원청': '홍천남산초등학교',
        },
        '남산초': {
            '강원특별자치도춘천교육지원청': '춘천남산초등학교',
            '강원특별자치도강릉교육지원청': '강릉남산초등학교',
            '강원특별자치도홍천교육지원청': '홍천남산초등학교',
        },
    }

    # 지역명 기반 학교명 검색 (역매핑)
    # 형식: {지역명: {학교약칭: 정식학교명}}
    REGION_SCHOOL_MAP = {
        '홍천': {
            '원당초': '홍천원당초등학교',
            '원당초등학교': '홍천원당초등학교',
            '반곡초': '홍천반곡초등학교',
            '반곡초등학교': '홍천반곡초등학교',
            '속초초': '홍천속초초등학교',
            '속초초등학교': '홍천속초초등학교',
            '남산초': '홍천남산초등학교',
            '남산초등학교': '홍천남산초등학교',
        },
        '양구': {
            '원당초': '양구원당초등학교',
            '원당초등학교': '양구원당초등학교',
        },
        '춘천': {
            '신동초': '춘천신동초등학교',
            '신동초등학교': '춘천신동초등학교',
            '교동초': '춘천교동초등학교',
            '교동초등학교': '춘천교동초등학교',
            '중앙초': '춘천중앙초등학교',
            '중앙초등학교': '춘천중앙초등학교',
            '조양초': '춘천조양초등학교',
            '조양초등학교': '춘천조양초등학교',
            '남산초': '춘천남산초등학교',
            '남산초등학교': '춘천남산초등학교',
        },
        '삼척': {
            '신동초': '삼척신동초등학교',
            '신동초등학교': '삼척신동초등학교',
            '중앙초': '삼척중앙초등학교',
            '중앙초등학교': '삼척중앙초등학교',
        },
        '원주': {
            '반곡초': '원주반곡초등학교',
            '반곡초등학교': '원주반곡초등학교',
            '교동초': '원주교동초등학교',
            '교동초등학교': '원주교동초등학교',
            '중앙초': '원주중앙초등학교',
            '중앙초등학교': '원주중앙초등학교',
        },
        '강릉': {
            '교동초': '강릉교동초등학교',
            '교동초등학교': '강릉교동초등학교',
            '중앙초': '강릉중앙초등학교',
            '중앙초등학교': '강릉중앙초등학교',
            '남산초': '강릉남산초등학교',
            '남산초등학교': '강릉남산초등학교',
        },
        '속초': {
            '교동초': '속초교동초등학교',
            '교동초등학교': '속초교동초등학교',
            '중앙초': '속초중앙초등학교',
            '중앙초등학교': '속초중앙초등학교',
            '조양초': '속초조양초등학교',
            '조양초등학교': '속초조양초등학교',
            '속초초': '속초초등학교',  # 속초는 그대로
            '속초초등학교': '속초초등학교',
        },
        '동해': {
            '중앙초': '동해중앙초등학교',
            '중앙초등학교': '동해중앙초등학교',
        },
    }

    # 학교 약칭 매핑 (순서 중요: 긴 것부터)
    SCHOOL_ABBR_MAPPINGS = {
        '공고': '공업고등학교',
        '정산고': '정보산업고등학교',
        '산과고': '산업과학고등학교',
        '여고': '여자고등학교',
        '여중': '여자중학교',
        '남고': '남자고등학교',
        '남중': '남자중학교',
        '상고': '상업고등학교',
        '농고': '농업고등학교',
        '공고': '공업고등학교',
        '과학고': '과학고등학교',
        '외고': '외국어고등학교',
        '예고': '예술고등학교',
        '체고': '체육고등학교',
        '고': '고등학교',
        '중': '중학교',
        '초': '초등학교',
    }

    # 직위명 정규화 매핑
    POSITION_NORMALIZATION = {
        '초등학교 교감': '교감',
        '중등학교 교감': '교감',
        '초등학교교감': '교감',
        '중등학교교감': '교감',
        '초등학교 교사': '교사',
        '중등학교 교사': '교사',
        '초등학교교사': '교사',
        '중등학교교사': '교사',
        '특수학교교사(초등)': '특수교사',
        '특수학교교사(중등)': '특수교사',
        '특수학교 교사(초등)': '특수교사',
        '특수학교 교사(중등)': '특수교사',
        '특수학교교사': '특수교사',
        '유치원 원감': '유치원감',
        '유치원원감': '유치원감',
    }

    def __init__(self, use_ai: bool = False, ai_matcher=None):
        """
        Args:
            use_ai: AI 기반 학교명 검증 사용 여부
            ai_matcher: GeminiMatcher 인스턴스 (use_ai=True일 때 필요)
        """
        self.use_ai = use_ai
        self.ai_matcher = ai_matcher

        if use_ai and not ai_matcher:
            try:
                from ai_matcher import GeminiMatcher
                import os
                self.ai_matcher = GeminiMatcher(api_key=os.getenv('GEMINI_API_KEY'))
                print("🤖 KFTA Parser: AI 모드 활성화")
            except Exception as e:
                print(f"⚠️  AI 모드 초기화 실패: {str(e)}")
                self.use_ai = False

    def is_region_name_only(self, text: str) -> bool:
        """텍스트가 지역명만 있는지 확인"""
        if pd.isna(text) or str(text).strip() == "":
            return False

        text = str(text).strip()

        # 지역명만 있는 패턴 (예: "춘천", "원주" 등)
        for region in self.GANGWON_REGIONS.keys():
            if text == region or text.endswith(region):
                return True

        return False

    def extract_region_from_text(self, text: str) -> Optional[str]:
        """텍스트에서 강원도 지역명 추출"""
        if pd.isna(text):
            return None

        text = str(text)

        for region in self.GANGWON_REGIONS.keys():
            if region in text:
                return region

        return None

    def get_education_office(self, region: str) -> str:
        """지역명으로 교육지원청명 가져오기"""
        return self.GANGWON_REGIONS.get(region, f'강원특별자치도{region}교육지원청')

    def find_education_office_for_school(self, school_name: str) -> str:
        """
        중고등학교명에서 교육지원청 찾기

        Args:
            school_name: 학교명 (예: "홍천여중", "강릉제일고")

        Returns:
            교육지원청명 (예: "강원특별자치도홍천교육지원청")
        """
        if pd.isna(school_name) or not school_name:
            return ''

        school_name = str(school_name).strip()

        # MIDDLE_HIGH_SCHOOL_REGION_MAP에서 키워드 매칭
        # 긴 키워드부터 매칭 (예: "강릉제일"이 "강릉"보다 먼저)
        sorted_keywords = sorted(self.MIDDLE_HIGH_SCHOOL_REGION_MAP.keys(),
                                key=len, reverse=True)

        for keyword in sorted_keywords:
            if keyword in school_name:
                return self.MIDDLE_HIGH_SCHOOL_REGION_MAP[keyword]

        return ''

    def lookup_school_with_region(self, region: str, school_name: str) -> tuple:
        """
        지역명과 학교명을 사용하여 정확한 학교명과 교육청 조회

        Args:
            region: 지역명 (예: "인제", "춘천", "양구")
            school_name: 학교명 또는 약칭 (예: "원당초", "월학초유")

        Returns:
            (교육청명, 정식학교명) 튜플
        """
        if not region or not school_name:
            return ('', school_name if school_name else '')

        # 1. 지역명에서 교육청 찾기
        education_office = self.get_education_office(region)

        # 2. 학교 약칭 확장 (예: "월학초유" => "월학초등학교")
        expanded_school = self.expand_school_abbreviation(school_name)

        # 3. REGION_SCHOOL_MAP에서 지역별 학교명 검색
        if region in self.REGION_SCHOOL_MAP:
            region_schools = self.REGION_SCHOOL_MAP[region]

            # 확장된 학교명으로 먼저 검색
            if expanded_school in region_schools:
                return (education_office, region_schools[expanded_school])

            # 원본 학교명으로 검색
            if school_name in region_schools:
                return (education_office, region_schools[school_name])

        # 4. GANGWON_SCHOOL_DATABASE에서 중복 학교명 검색
        if expanded_school in self.GANGWON_SCHOOL_DATABASE:
            school_mappings = self.GANGWON_SCHOOL_DATABASE[expanded_school]
            if education_office in school_mappings:
                return (education_office, school_mappings[education_office])

        if school_name in self.GANGWON_SCHOOL_DATABASE:
            school_mappings = self.GANGWON_SCHOOL_DATABASE[school_name]
            if education_office in school_mappings:
                return (education_office, school_mappings[education_office])

        # 5. 매핑이 없으면 확장된 학교명 그대로 반환
        return (education_office, expanded_school)

    def is_school_name(self, text: str) -> bool:
        """
        텍스트가 학교명인지 판단

        Args:
            text: 확인할 텍스트

        Returns:
            학교명이면 True, 아니면 False
        """
        if pd.isna(text) or not text:
            return False

        text = str(text).strip()

        # 학교명 패턴 (초등학교, 중학교, 고등학교, 유치원 등)
        school_patterns = [
            '초등학교', '중학교', '고등학교', '유치원',
            '초교', '중교', '고교',
            '여중', '여고', '남중', '남고',
            '공고', '상고', '농고', '정산고', '산과고',
        ]

        # 패턴 매칭
        for pattern in school_patterns:
            if pattern in text:
                return True

        # 끝나는 패턴 확인 (예: "춘천중", "원주고", "남산초", "속초유")
        if text.endswith('초') or text.endswith('중') or text.endswith('고') or text.endswith('유'):
            # 단, 한 글자는 제외 (예: "초", "유"만 있는 경우)
            if len(text) > 1:
                return True

        # 병설유치원 패턴
        if '병설유' in text or '초유' in text:
            return True

        # 정규표현식 패턴: 지역명(학교급) 형식
        # 예: 인제(고), 춘천(중), 속초(초), 원주(유)
        import re
        pattern = r'^[\w가-힣]+\((초|중|고|유)\)$'
        if re.match(pattern, text):
            return True

        return False

    def expand_school_abbreviation(self, school_name: str) -> str:
        """
        학교 약칭을 정식 명칭으로 확장
        예: "춘천공고" → "춘천공업고등학교"
            "원주여고" → "원주여자고등학교"
            "춘천OO초" → "춘천OO초등학교"
            "신림초/교사" → "신림초등학교"
            "OO초병설유치원" → "OO초등학교"
            "속초유" → "속초유치원" (예외)
            "인제(고)" → "인제고등학교"
            "춘천(중)" → "춘천중학교"
            "속초(유)" → "속초유치원"
        """
        if pd.isna(school_name) or not school_name:
            return school_name

        school_name = str(school_name).strip()

        # 0. 정규표현식 패턴 처리: 지역명(학교급) 형식
        # 예: 인제(고) → 인제고등학교
        import re
        pattern = r'^([\w가-힣]+)\((초|중|고|유)\)$'
        match = re.match(pattern, school_name)
        if match:
            base_name = match.group(1)
            school_type = match.group(2)

            type_mapping = {
                '초': '초등학교',
                '중': '중학교',
                '고': '고등학교',
                '유': '유치원'
            }

            return base_name + type_mapping.get(school_type, '')

        # 1. /교사, /교장 등 직위 표기 제거
        if '/' in school_name:
            school_name = school_name.split('/')[0].strip()

        # 2. 병설유치원 처리
        # OO초병설유치원 → OO초등학교
        # OO초 병설유치원 → OO초등학교
        # OO초 병설유 → OO초등학교
        # OO초병설유 → OO초등학교
        # OO초유 → OO초등학교 (단, 속초유는 예외)
        byeongseol_patterns = [
            '병설유치원',
            ' 병설유치원',
            ' 병설유',
            '병설유',
        ]

        for pattern in byeongseol_patterns:
            if pattern in school_name:
                school_name = school_name.replace(pattern, '')
                # 초로 끝나면 초등학교로 확장
                if school_name.endswith('초'):
                    return school_name + '등학교'
                return school_name

        # OO초유 → OO초등학교 (단, 속초유는 예외)
        if school_name.endswith('초유') and not school_name == '속초유':
            return school_name[:-2] + '초등학교'

        # 속초유 → 속초유치원 (예외 처리)
        if school_name == '속초유':
            return '속초유치원'

        # 3. 약칭 매핑을 길이 순으로 정렬 (긴 것부터 매칭)
        sorted_mappings = sorted(self.SCHOOL_ABBR_MAPPINGS.items(),
                                key=lambda x: len(x[0]),
                                reverse=True)

        for abbr, full_name in sorted_mappings:
            if school_name.endswith(abbr):
                # 약칭을 정식 명칭으로 교체
                base_name = school_name[:-len(abbr)]
                return base_name + full_name

        return school_name

    def parse_abbreviated_school_format(self, school_text: str) -> tuple:
        """
        약식 학교명 파싱: "□□ OO초" 형식

        Args:
            school_text: "춘천 남산초" 또는 "춘천남산초" 형식

        Returns:
            (교육청명, 학교풀네임) 튜플
            예: ("강원특별자치도춘천교육지원청", "남산초등학교")

        중요: 지역명 뒤에 공백이 있을 때만 지역명을 교육청으로 분리
              예: "춘천 남산초" → (춘천교육청, "남산초등학교")
                  "동해중앙초" → ("", "동해중앙초등학교")
                  "동해중학교" → ("", "동해중학교")
        """
        if pd.isna(school_text) or not school_text:
            return ('', school_text)

        school_text = str(school_text).strip()

        region = None
        school_name = school_text
        education_office = ''

        # 강원도 지역명 찾기 (공백이 있는 경우만 분리)
        for region_name in self.GANGWON_REGIONS.keys():
            if school_text.startswith(region_name + ' '):  # 지역명 뒤에 공백이 있는 경우만
                region = region_name
                # 지역명과 공백 제거
                remainder = school_text[len(region_name):].strip()
                if remainder:
                    school_name = remainder
                    education_office = self.get_education_office(region)
                break

        # 학교 약칭 확장
        school_name = self.expand_school_abbreviation(school_name)

        return (education_office, school_name)

    def normalize_position(self, position: str) -> str:
        """
        직위명 정규화

        Args:
            position: 원본 직위명

        Returns:
            정규화된 직위명
        """
        if pd.isna(position) or not position:
            return position

        position = str(position).strip()

        # 정규화 매핑에서 찾기
        return self.POSITION_NORMALIZATION.get(position, position)

    def verify_and_expand_with_ai(self, school_name: str) -> tuple:
        """
        AI를 사용하여 학교명 검증 및 확장

        Args:
            school_name: 학교명

        Returns:
            (교육청명, 학교풀네임) 튜플
        """
        if not self.use_ai or not self.ai_matcher:
            # AI 미사용 시 기본 처리
            return self.parse_abbreviated_school_format(school_name)

        try:
            result = self.ai_matcher.verify_and_expand_school_name(
                school_name,
                self.GANGWON_REGIONS
            )

            full_name = result.get('full_name', school_name)
            education_office = result.get('education_office', '')
            confidence = result.get('confidence', 0)

            # 신뢰도가 낮으면 기본 처리로 fallback
            if confidence < 50:
                return self.parse_abbreviated_school_format(school_name)

            if confidence >= 70:
                print(f"  🤖 AI 검증: '{school_name}' → '{full_name}' (신뢰도: {confidence}%)")

            return (education_office, full_name)

        except Exception as e:
            print(f"  ⚠️  AI 검증 실패, 기본 모드로 전환: {str(e)}")
            return self.parse_abbreviated_school_format(school_name)

    def parse_bigo_for_kindergarten(self, bigo_text: str) -> tuple:
        """
        유치원 신규원감 발령의 비고란 파싱

        Args:
            bigo_text: 비고란 텍스트 (예: "인제 월학초유 교사", "강원특별자치도교육청 유아교육과")

        Returns:
            (현재교육청, 현재분회) 튜플
        """
        if pd.isna(bigo_text) or not bigo_text:
            return ('', '')

        bigo_text = str(bigo_text).strip()

        # 특수 케이스: "강원특별자치도교육청" 으로 시작하는 경우
        if bigo_text.startswith('강원특별자치도교육청'):
            return ('강원특별자치도춘천교육지원청', '강원특별자치도교육청')

        # 일반 케이스: "지역명 학교명 직위" 형식
        # 예: "인제 월학초유 교사"

        # 지역명 추출 (공백으로 구분)
        parts = bigo_text.split()
        if len(parts) >= 2:
            # 첫 번째 부분이 지역명인지 확인
            potential_region = parts[0]

            if potential_region in self.GANGWON_REGIONS:
                # 지역명 발견
                education_office = self.get_education_office(potential_region)

                # 나머지 부분에서 학교명 추출 (직위 제거)
                school_parts = parts[1:]
                school_text = ' '.join(school_parts)

                # 직위 키워드 제거 ("교사", "교장" 등)
                position_keywords = ['교사', '교장', '교감', '원장', '원감']
                for keyword in position_keywords:
                    if school_text.endswith(keyword):
                        school_text = school_text[:-len(keyword)].strip()
                        break

                # 학교명 확장 및 데이터베이스 검색
                edu_office, full_school_name = self.lookup_school_with_region(
                    potential_region,
                    school_text
                )

                return (edu_office, full_school_name)

        # 지역명 없이 학교명만 있는 경우 (예: "월학초유")
        # 직위 키워드 제거
        clean_text = bigo_text
        position_keywords = ['교사', '교장', '교감', '원장', '원감']
        for keyword in position_keywords:
            if clean_text.endswith(keyword):
                clean_text = clean_text[:-len(keyword)].strip()
                break

        # 학교 약칭 확장
        expanded_school = self.expand_school_abbreviation(clean_text)
        return ('', expanded_school)

    def is_valid_data_row(self, row: pd.Series, name_col_idx: int = 2) -> bool:
        """
        유효한 데이터 행인지 확인
        3번째 열(인덱스 2)이 헤더 키워드가 아니고 빈값도 아니면 True
        """
        if len(row) <= name_col_idx:
            return False

        value = row.iloc[name_col_idx]

        # NaN이거나 빈 문자열이면 False
        if pd.isna(value) or str(value).strip() == "":
            return False

        # 헤더 키워드 목록 (대응, 성명, 이름 등)
        header_keywords = ['성명', '이름', '대응', '대 응']
        value_str = str(value).strip()

        # 헤더 키워드와 정확히 일치하면 헤더 행으로 판단
        if value_str in header_keywords:
            return False

        # 추가: 비고 컬럼 확인 (4번째 열, 인덱스 3)
        # 비고 컬럼이 "비고"라는 텍스트를 포함하면 헤더로 판단
        if len(row) > 3:
            bigo_value = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ""
            if '비고' in bigo_value and '전소속' in bigo_value:
                return False

        return True

    def parse_row_to_kfta(self, row: pd.Series) -> Dict[str, str]:
        """
        행 데이터를 강원교총 표준 형식으로 변환

        필드 매핑:
        - 3번째 필드(인덱스 2) → 이름 (성명)
        - 5번째 필드(인덱스 4) → 직위 (정규화 적용)
        - 6번째 필드(인덱스 5) → 발령분회 (약칭 확장)
        - 6번째 필드의 지역명 → 발령교육청
        - 8번째 필드(인덱스 7) → 현재분회 (조건부, 약칭 확장)
        - 9번째 필드(인덱스 8) → 현재교육청/현재분회 참고
        """
        result = {
            '현재교육청': '',
            '현재분회': '',
            '이름': '',
            '발령교육청': '',
            '발령분회': '',
            '과목': '',
            '직위': '',
            '직종분류': '',
            '분류명': '',
            '취급코드': '',
            '시군구분': '',
            '교호기호등': '',
        }

        # 3번째 필드 → 이름 (성명)
        if len(row) > 2:
            result['이름'] = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''

        # 5번째 필드 → 직위 (정규화 적용)
        if len(row) > 4:
            position = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''
            result['직위'] = self.normalize_position(position)

        # 6번째 필드 → 발령분회 및 발령교육청
        if len(row) > 5:
            field_6 = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ''

            # 중고등학교는 AI 검증 우선 시도 (use_ai=True인 경우)
            is_middle_high = '중학' in field_6 or '고등' in field_6 or field_6.endswith('중') or field_6.endswith('고')

            if is_middle_high and self.use_ai:
                # AI로 학교명 검증 및 확장
                edu_office, school_name = self.verify_and_expand_with_ai(field_6)
                if edu_office:
                    result['발령교육청'] = edu_office
                    result['발령분회'] = school_name
                else:
                    result['발령분회'] = school_name
            else:
                # "□□ OO초" 형식 파싱
                edu_office, school_name = self.parse_abbreviated_school_format(field_6)

                if edu_office:  # 약식 형식으로 파싱 성공
                    result['발령교육청'] = edu_office
                    result['발령분회'] = school_name
                else:
                    # 일반 형식 처리
                    result['발령분회'] = self.expand_school_abbreviation(field_6)

                    # 중고등학교 교육지원청 자동 매핑
                    if is_middle_high:
                        edu_office = self.find_education_office_for_school(result['발령분회'])
                        if edu_office:
                            result['발령교육청'] = edu_office
                    else:
                        # 초등학교는 지역명 추출 → 발령교육청
                        region = self.extract_region_from_text(field_6)
                        if region:
                            result['발령교육청'] = self.get_education_office(region)

        # 8번째 필드 처리
        if len(row) > 7:
            field_8 = str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else ''

            # 유치원 신규원감 발령 특수 처리
            # 직위에 "유치원"과 "원감" 또는 "신규"가 포함된 경우
            is_kindergarten_principal = False
            if result['직위']:
                position_lower = result['직위'].lower()
                is_kindergarten = '유치원' in position_lower
                is_principal = '원감' in position_lower or '신규' in position_lower
                is_kindergarten_principal = is_kindergarten and is_principal

            if is_kindergarten_principal and len(row) > 9:
                # 유치원 신규원감의 경우 비고란(10번째 필드)에서 현재분회 정보 추출
                field_10 = str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else ''

                if field_10:
                    edu_office, school_name = self.parse_bigo_for_kindergarten(field_10)
                    if edu_office:
                        result['현재교육청'] = edu_office
                    if school_name:
                        result['현재분회'] = school_name

                    # 디버그 메시지 (선택사항)
                    # print(f"  🏫 유치원 신규원감 파싱: '{field_10}' → 교육청={edu_office}, 분회={school_name}")

            # 8번째 필드가 지역명만 있는 경우 (일반 케이스)
            elif self.is_region_name_only(field_8):
                # 10번째 필드(인덱스 9) 참고 - 비고란에 실제 학교명
                if len(row) > 9:
                    field_10 = str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else ''

                    if field_10:  # 비고에 학교명이 있으면
                        # 학교 약칭 확장
                        school_name = self.expand_school_abbreviation(field_10)
                        result['현재분회'] = school_name

                        # 중고등학교 교육지원청 자동 매핑
                        edu_office = self.find_education_office_for_school(school_name)
                        if edu_office:
                            result['현재교육청'] = edu_office
                        else:
                            # 매핑 실패 시 8번째 필드의 지역명 사용
                            region_8 = self.extract_region_from_text(field_8)
                            if region_8:
                                result['현재교육청'] = self.get_education_office(region_8)
                    else:
                        # 비고가 없으면 8번째 필드의 지역명만 사용
                        region_8 = self.extract_region_from_text(field_8)
                        if region_8:
                            result['현재교육청'] = self.get_education_office(region_8)
            else:
                # 중고등학교는 AI 검증 우선 시도
                is_middle_high = '중학' in field_8 or '고등' in field_8 or field_8.endswith('중') or field_8.endswith('고')

                if is_middle_high and self.use_ai:
                    # AI로 학교명 검증 및 확장
                    edu_office, school_name = self.verify_and_expand_with_ai(field_8)
                    if edu_office:
                        result['현재교육청'] = edu_office
                        result['현재분회'] = school_name
                    else:
                        result['현재분회'] = school_name
                else:
                    # "□□ OO초" 형식 파싱
                    edu_office, school_name = self.parse_abbreviated_school_format(field_8)

                    if edu_office:  # 약식 형식으로 파싱 성공
                        result['현재교육청'] = edu_office
                        result['현재분회'] = school_name
                    else:
                        # 8번째 필드가 지역명만이 아니면 → 현재분회
                        result['현재분회'] = self.expand_school_abbreviation(field_8)

                        # 중고등학교 교육지원청 자동 매핑
                        if is_middle_high:
                            edu_office = self.find_education_office_for_school(result['현재분회'])
                            if edu_office:
                                result['현재교육청'] = edu_office
                        else:
                            # 초등학교는 8번째 필드에서 지역명 추출 → 현재교육청
                            region = self.extract_region_from_text(field_8)
                            if region:
                                result['현재교육청'] = self.get_education_office(region)

        # 9번째 필드 → 과목 처리 (학교명 감지 및 이동)
        # 이 부분은 발령분회/현재분회가 모두 처리된 후에 실행됨
        if len(row) > 8:
            subject_field = str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) else ''

            if subject_field:
                # 학교명인지 확인
                if self.is_school_name(subject_field):
                    # 학교명을 올바른 형식으로 확장
                    school_name = self.expand_school_abbreviation(subject_field)

                    # 교육지원청 찾기
                    edu_office = self.find_education_office_for_school(school_name)

                    # 발령분회가 비어있으면 발령분회로 이동
                    if not result['발령분회']:
                        result['발령분회'] = school_name
                        if edu_office:
                            result['발령교육청'] = edu_office
                    # 현재분회가 비어있으면 현재분회로 이동
                    elif not result['현재분회']:
                        result['현재분회'] = school_name
                        if edu_office:
                            result['현재교육청'] = edu_office
                    # 둘 다 채워져 있으면 과목으로 유지 (예외 케이스)
                    else:
                        result['과목'] = subject_field

                    # 과목 필드는 빈 문자열로 (학교명이 이동되었으므로)
                    if result['발령분회'] == school_name or result['현재분회'] == school_name:
                        result['과목'] = ''
                else:
                    # 학교명이 아니면 과목으로 그대로 유지
                    result['과목'] = subject_field

        # ===== 최종 검증 및 정리 =====
        # 모든 필드를 검사하여 학교명이 잘못된 위치에 있으면 올바른 위치로 이동

        # 1. 과목 외의 다른 필드에서 학교명 검사
        fields_to_check = ['직종분류', '분류명', '취급코드', '시군구분', '교호기호등']

        for field_name in fields_to_check:
            field_value = result.get(field_name, '')
            if field_value and self.is_school_name(field_value):
                # 학교명을 올바른 형식으로 확장
                school_name = self.expand_school_abbreviation(field_value)
                edu_office = self.find_education_office_for_school(school_name)

                # 발령분회가 비어있으면 발령분회로 이동
                if not result['발령분회']:
                    result['발령분회'] = school_name
                    if edu_office:
                        result['발령교육청'] = edu_office
                    result[field_name] = ''  # 원본 필드는 비우기
                # 현재분회가 비어있으면 현재분회로 이동
                elif not result['현재분회']:
                    result['현재분회'] = school_name
                    if edu_office:
                        result['현재교육청'] = edu_office
                    result[field_name] = ''  # 원본 필드는 비우기

        # 2. 발령분회가 있으면 발령교육청 자동 채우기 (아직 비어있는 경우)
        if result['발령분회'] and not result['발령교육청']:
            edu_office = self.find_education_office_for_school(result['발령분회'])
            if not edu_office:
                # 지역명 추출 시도
                region = self.extract_region_from_text(result['발령분회'])
                if region:
                    edu_office = self.get_education_office(region)
            if edu_office:
                result['발령교육청'] = edu_office

        # 3. 현재분회가 있으면 현재교육청 자동 채우기 (아직 비어있는 경우)
        if result['현재분회'] and not result['현재교육청']:
            edu_office = self.find_education_office_for_school(result['현재분회'])
            if not edu_office:
                # 지역명 추출 시도
                region = self.extract_region_from_text(result['현재분회'])
                if region:
                    edu_office = self.get_education_office(region)
            if edu_office:
                result['현재교육청'] = edu_office

        # 4. 교육청 이름이 잘못된 필드에 있으면 제거
        # 교육청은 현재교육청, 발령교육청에만 들어가야 함
        education_office_keywords = ['교육청', '교육지원청']

        for field_name in ['이름', '발령분회', '현재분회', '과목', '직위', '직종분류', '분류명', '취급코드', '시군구분', '교호기호등']:
            field_value = result.get(field_name, '')
            if field_value:
                # 교육청 키워드가 있는지 확인
                has_edu_office = any(keyword in field_value for keyword in education_office_keywords)

                if has_edu_office:
                    # 발령교육청이 비어있으면 이동
                    if not result['발령교육청']:
                        result['발령교육청'] = field_value
                        result[field_name] = ''
                    # 현재교육청이 비어있으면 이동
                    elif not result['현재교육청']:
                        result['현재교육청'] = field_value
                        result[field_name] = ''
                    # 둘 다 채워져 있으면 현재 필드에서 제거만
                    else:
                        result[field_name] = ''

        return result

    def parse_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        DataFrame 전체를 파싱하여 강원교총 표준 형식으로 변환
        """
        parsed_rows = []

        for idx, row in df.iterrows():
            # 유효한 데이터 행만 처리
            if self.is_valid_data_row(row):
                parsed_data = self.parse_row_to_kfta(row)
                parsed_rows.append(parsed_data)

        return pd.DataFrame(parsed_rows)
