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

    def __init__(self):
        pass

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
        - 5번째 필드(인덱스 4) → 직위
        - 6번째 필드(인덱스 5) → 발령본청
        - 6번째 필드의 지역명 → 발령교육청
        - 8번째 필드(인덱스 7) → 현재본청 (조건부)
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

        # 5번째 필드 → 직위
        if len(row) > 4:
            result['직위'] = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''

        # 6번째 필드 → 발령본청 및 발령교육청
        if len(row) > 5:
            field_6 = str(row.iloc[5]).strip() if pd.notna(row.iloc[5]) else ''
            result['발령본청'] = field_6

            # 6번째 필드에서 지역명 추출 → 발령교육청
            region = self.extract_region_from_text(field_6)
            if region:
                result['발령교육청'] = self.get_education_office(region)

        # 8번째 필드 처리
        if len(row) > 7:
            field_8 = str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else ''

            # 8번째 필드가 지역명만 있는 경우
            if self.is_region_name_only(field_8):
                # 9번째 필드 참고
                if len(row) > 8:
                    field_9 = str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) else ''

                    # 9번째 필드에서 교육청과 본청 추출
                    region_9 = self.extract_region_from_text(field_9)
                    if region_9:
                        result['현재교육청'] = self.get_education_office(region_9)
                        result['현재본청'] = field_9
                    else:
                        # 8번째 필드의 지역명 사용
                        region_8 = self.extract_region_from_text(field_8)
                        if region_8:
                            result['현재교육청'] = self.get_education_office(region_8)
            else:
                # 8번째 필드가 지역명만이 아니면 → 현재본청
                result['현재본청'] = field_8

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
