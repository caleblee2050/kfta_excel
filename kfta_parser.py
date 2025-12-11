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

    # 타시도 지역명 (강원도 외 지역)
    OTHER_REGIONS = [
        '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종',
        '경기', '충북', '충남', '전북', '전남', '경북', '경남', '제주'
    ]

    # 특정 학교 매핑 데이터베이스 (정확한 정보가 필요한 학교들)
    SPECIFIC_SCHOOL_MAPPINGS = {
        # 춘천 지역
        '동산중학교': ('강원특별자치도춘천교육지원청', '동산중학교'),
        '춘천동산중학교': ('강원특별자치도춘천교육지원청', '동산중학교'),
        '동내초등학교': ('강원특별자치도춘천교육지원청', '동내초등학교'),
        '금병초등학교': ('강원특별자치도춘천교육지원청', '금병초등학교'),
        '송화초등학교': ('강원특별자치도춘천교육지원청', '송화초등학교'),
        '지촌초등학교': ('강원특별자치도춘천교육지원청', '지촌초등학교'),
        '창촌중학교': ('강원특별자치도춘천교육지원청', '창촌중학교'),
        '강서중학교': ('강원특별자치도춘천교육지원청', '강서중학교'),
        '우석중학교': ('강원특별자치도춘천교육지원청', '우석중학교'),
        '만천유치원': ('강원특별자치도춘천교육지원청', '만천유치원'),
        '봄봄유치원': ('강원특별자치도춘천교육지원청', '봄봄유치원'),
        '새봄유치원': ('강원특별자치도춘천교육지원청', '새봄유치원'),
        '온의유치원': ('강원특별자치도춘천교육지원청', '온의유치원'),

        # 원주 지역
        '동광산과고': ('강원특별자치도원주교육지원청', '동광산업과학고등학교'),
        '동광산업과학고등학교': ('강원특별자치도원주교육지원청', '동광산업과학고등학교'),
        '강원생명과학고등학교': ('강원특별자치도원주교육지원청', '강원생명과학고등학교'),
    }

    # 학교 약칭 매핑
    SCHOOL_ABBR_MAPPINGS = {
        '공고': '공업고등학교',
        '정산고': '정보산업고등학교',
        '산과고': '산업과학고등학교',
        '여고': '여자고등학교',
        '여중': '여자중학교',
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

    def expand_school_abbreviation(self, school_name: str) -> str:
        """
        학교 약칭을 정식 명칭으로 확장
        예: "춘천공고" → "춘천공업고등학교"
            "원주여고" → "원주여자고등학교"
            "춘천OO초" → "춘천OO초등학교"
        """
        if pd.isna(school_name) or not school_name:
            return school_name

        school_name = str(school_name).strip()

        # 약칭 매핑을 길이 순으로 정렬 (긴 것부터 매칭)
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
        """
        if pd.isna(school_text) or not school_text:
            return ('', school_text)

        school_text = str(school_text).strip()
        original_school_text = school_text

        # 1단계: 특정 학교 매핑 우선 체크
        if school_text in self.SPECIFIC_SCHOOL_MAPPINGS:
            return self.SPECIFIC_SCHOOL_MAPPINGS[school_text]

        # 약칭 확장 후 다시 체크
        expanded = self.expand_school_abbreviation(school_text)
        if expanded in self.SPECIFIC_SCHOOL_MAPPINGS:
            return self.SPECIFIC_SCHOOL_MAPPINGS[expanded]

        # 2단계: 타시도 지역 체크
        for other_region in self.OTHER_REGIONS:
            if school_text.startswith(other_region):
                # 타시도 학교는 교육지원청 없음
                remainder = school_text[len(other_region):].strip()
                if remainder:
                    school_name = self.expand_school_abbreviation(remainder)
                    return ('', school_name)  # 교육지원청 빈 문자열
                break

        # 3단계: 강원도 지역명 체크 - 공백이 있는 경우에만 지역명으로 인식
        region = None
        school_name = school_text

        for region_name in self.GANGWON_REGIONS.keys():
            # 패턴 1: "지역명 학교명" (공백 있음) - 지역명 제거
            if school_text.startswith(region_name + ' '):
                region = region_name
                remainder = school_text[len(region_name):].strip()
                if remainder:
                    school_name = remainder
                break
            # 패턴 2: "지역명OO초/중/고" (공백 없고 학교명이 짧음) - 약칭 형식
            # 예: "춘천남산초" (O), "춘천교대부설초등학교" (X - 실제 학교명)
            elif school_text.startswith(region_name):
                # 지역명 제거 후 남은 부분
                remainder = school_text[len(region_name):]
                # 남은 부분이 짧고 (10자 이하) 초/중/고/유로 끝나면 약칭으로 간주
                if remainder and len(remainder) <= 10 and any(remainder.endswith(x) for x in ['초', '중', '고', '유']):
                    region = region_name
                    school_name = remainder
                    break

        # 학교 약칭 확장
        school_name = self.expand_school_abbreviation(school_name)

        # 교육청명 생성
        education_office = ''
        if region:
            education_office = self.get_education_office(region)

        return (education_office, school_name)

    def clean_school_name(self, school_name: str) -> str:
        """
        학교명에서 불필요한 텍스트 제거

        Args:
            school_name: 원본 학교명

        Returns:
            정리된 학교명
        """
        if pd.isna(school_name) or not school_name:
            return school_name

        school_name = str(school_name).strip()

        # 제거할 패턴 리스트 (학교명 뒤에 붙는 추가 정보)
        patterns_to_remove = [
            ' 전문상담', '전문상담',
            ' 보건', '보건',
            ' 영양', '영양',
            ' 사서', '사서',
            ' 특수', '특수',
            ' 상담', '상담',
            ' (전문상담)', '(전문상담)',
            ' (보건)', '(보건)',
        ]

        for pattern in patterns_to_remove:
            if school_name.endswith(pattern):
                school_name = school_name[:-len(pattern)].strip()
                break

        return school_name

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

    def is_valid_data_row(self, row: pd.Series, name_col_idx: int = 2) -> bool:
        """
        유효한 데이터 행인지 확인
        3번째 열(인덱스 2)이 '성명'이 아니고 빈값도 아니면 True
        """
        if len(row) <= name_col_idx:
            return False

        value = row.iloc[name_col_idx]

        # NaN이거나 빈 문자열이면 False
        if pd.isna(value) or str(value).strip() == "":
            return False

        # '성명'이면 헤더 행이므로 False
        if str(value).strip() == '성명':
            return False

        return True

    def parse_row_to_kfta(self, row: pd.Series) -> Dict[str, str]:
        """
        행 데이터를 강원교총 표준 형식으로 변환

        필드 매핑:
        - 3번째 필드(인덱스 2) → 대응 (성명)
        - 5번째 필드(인덱스 4) → 직위 (정규화 적용)
        - 6번째 필드(인덱스 5) → 발령본청 (약칭 확장)
        - 6번째 필드의 지역명 → 발령교육청
        - 8번째 필드(인덱스 7) → 현재본청 (조건부, 약칭 확장)
        - 9번째 필드(인덱스 8) → 현재교육청/현재본청 참고
        """
        result = {
            '현재교육청': '',
            '현재본청': '',
            '대응': '',
            '발령교육청': '',
            '발령본청': '',
            '과목': '',
            '직위': '',
            '직종분류': '',
            '분류명': '',
            '취급코드': '',
            '시군구분': '',
            '교호기호등': '',
        }

        # 3번째 필드 → 대응 (성명)
        if len(row) > 2:
            result['대응'] = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''

        # 5번째 필드 → 직위 (정규화 적용)
        if len(row) > 4:
            position = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''
            result['직위'] = self.normalize_position(position)

        # 6번째 필드 → 발령본청 및 발령교육청
        if len(row) > 5:
            field_6 = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ''
            # 불필요한 텍스트 제거 (전문상담, 보건 등)
            field_6 = self.clean_school_name(field_6)

            # 중고등학교는 AI 검증 우선 시도 (use_ai=True인 경우)
            is_middle_high = '중학' in field_6 or '고등' in field_6 or field_6.endswith('중') or field_6.endswith('고')

            if is_middle_high and self.use_ai:
                # AI로 학교명 검증 및 확장
                edu_office, school_name = self.verify_and_expand_with_ai(field_6)
                if edu_office:
                    result['발령교육청'] = edu_office
                    result['발령본청'] = school_name
                else:
                    result['발령본청'] = school_name
            else:
                # "□□ OO초" 형식 파싱
                edu_office, school_name = self.parse_abbreviated_school_format(field_6)

                if edu_office:  # 약식 형식으로 파싱 성공
                    result['발령교육청'] = edu_office
                    result['발령본청'] = school_name
                else:
                    # 일반 형식 처리
                    result['발령본청'] = self.expand_school_abbreviation(field_6)

                    # 지역명 추출 → 발령교육청
                    region = self.extract_region_from_text(field_6)
                    if region:
                        result['발령교육청'] = self.get_education_office(region)

        # 8번째 필드 처리
        if len(row) > 7:
            field_8 = str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else ''
            # 불필요한 텍스트 제거
            field_8 = self.clean_school_name(field_8)

            # 8번째 필드가 지역명만 있는 경우
            if self.is_region_name_only(field_8):
                # 9번째 필드 참고
                if len(row) > 8:
                    field_9 = str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) else ''
                    # 불필요한 텍스트 제거
                    field_9 = self.clean_school_name(field_9)

                    # "□□ OO초" 형식 파싱
                    edu_office, school_name = self.parse_abbreviated_school_format(field_9)

                    if edu_office:  # 약식 형식으로 파싱 성공
                        result['현재교육청'] = edu_office
                        result['현재본청'] = school_name
                    else:
                        # 9번째 필드에서 교육청과 본청 추출
                        region_9 = self.extract_region_from_text(field_9)
                        if region_9:
                            result['현재교육청'] = self.get_education_office(region_9)
                            result['현재본청'] = self.expand_school_abbreviation(field_9)
                        else:
                            # 8번째 필드의 지역명 사용
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
                        result['현재본청'] = school_name
                    else:
                        result['현재본청'] = school_name
                else:
                    # "□□ OO초" 형식 파싱
                    edu_office, school_name = self.parse_abbreviated_school_format(field_8)

                    if edu_office:  # 약식 형식으로 파싱 성공
                        result['현재교육청'] = edu_office
                        result['현재본청'] = school_name
                    else:
                        # 8번째 필드가 지역명만이 아니면 → 현재본청
                        result['현재본청'] = self.expand_school_abbreviation(field_8)

                        # 8번째 필드에서 지역명 추출 → 현재교육청
                        region = self.extract_region_from_text(field_8)
                        if region:
                            result['현재교육청'] = self.get_education_office(region)

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
