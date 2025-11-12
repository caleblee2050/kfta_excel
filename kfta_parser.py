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

    def expand_school_abbreviation(self, school_name: str) -> str:
        """
        학교 약칭을 정식 명칭으로 확장
        예: "춘천공고" → "춘천공업고등학교"
            "원주여고" → "원주여자고등학교"
            "춘천OO초" → "춘천OO초등학교"
            "신림초/교사" → "신림초등학교"
            "OO초병설유치원" → "OO초등학교"
            "속초유" → "속초유치원" (예외)
        """
        if pd.isna(school_name) or not school_name:
            return school_name

        school_name = str(school_name).strip()

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

        # 9번째 필드 → 과목 (중등교사 전용)
        if len(row) > 8:
            subject = str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) else ''
            result['과목'] = subject

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

            # 8번째 필드가 지역명만 있는 경우
            if self.is_region_name_only(field_8):
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
