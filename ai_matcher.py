#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 유사도 매칭 모듈
Google Gemini API를 활용한 의미론적 유사도 분석
"""

import google.generativeai as genai
import os
from typing import List, Dict, Tuple, Optional
import json
from functools import lru_cache
import time


class GeminiMatcher:
    """Gemini AI를 활용한 스마트 매칭"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Gemini Matcher 초기화

        Args:
            api_key: Gemini API 키 (없으면 환경변수에서 읽음)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Gemini API 키가 필요합니다. "
                "GEMINI_API_KEY 환경변수를 설정하거나 api_key 파라미터를 전달하세요."
            )

        # Gemini 초기화
        genai.configure(api_key=self.api_key)
        # 최신 안정 모델 사용
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # 캐시 (같은 요청 반복 방지)
        self.cache = {}

    @lru_cache(maxsize=1000)
    def calculate_semantic_similarity(
        self,
        text1: str,
        text2: str,
        context: str = "엑셀 컬럼명"
    ) -> Dict[str, any]:
        """
        AI를 사용하여 두 텍스트의 의미론적 유사도 계산

        Args:
            text1: 첫 번째 텍스트
            text2: 두 번째 텍스트
            context: 컨텍스트 (컬럼명, 값 등)

        Returns:
            {
                'similarity': 0-100 사이의 유사도 점수,
                'is_similar': 유사 여부 (bool),
                'reason': 판단 이유,
                'mapping': 매칭 제안
            }
        """
        # 캐시 확인
        cache_key = f"{text1}||{text2}||{context}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Gemini에게 질문
        prompt = f"""
당신은 엑셀 데이터 분석 전문가입니다. 두 텍스트가 같은 의미인지 판단해주세요.

**컨텍스트**: {context}

**텍스트 1**: "{text1}"
**텍스트 2**: "{text2}"

다음 기준으로 판단하세요:
1. 동일한 의미를 가지는가? (예: "이름"과 "성명", "학교"와 "대학교")
2. 유사한 개념인가? (예: "전공"과 "전공분야")
3. 다국어 표현인가? (예: "name"과 "이름")
4. 약어와 전체 표현인가? (예: "HP"와 "휴대폰", "email"과 "이메일")
5. 한자와 한글 표현인가? (예: "大學"과 "대학")

**응답 형식** (JSON):
{{
    "similarity": 0-100 사이의 숫자 (100이 완전 동일),
    "is_similar": true 또는 false (유사도 70 이상이면 true),
    "reason": "판단 이유를 한국어로 설명",
    "mapping": "통일된 표현 제안"
}}

JSON만 출력하세요. 다른 설명은 불필요합니다.
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # JSON 파싱
            # Gemini가 ```json ``` 로 감쌀 수 있으므로 제거
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            result = json.loads(result_text)

            # 캐시에 저장
            self.cache[cache_key] = result

            return result

        except Exception as e:
            print(f"⚠️  AI 분석 실패 ({text1} ↔ {text2}): {str(e)}")
            # 실패 시 기본값 반환
            return {
                'similarity': 0,
                'is_similar': False,
                'reason': f'AI 분석 실패: {str(e)}',
                'mapping': text1
            }

    def match_columns_batch(
        self,
        columns_list: List[List[str]]
    ) -> Dict[str, List[str]]:
        """
        여러 파일의 컬럼들을 일괄 매칭

        Args:
            columns_list: 각 파일의 컬럼 리스트들

        Returns:
            {통합컬럼명: [원본컬럼명들]}
        """
        print("\n🤖 AI 기반 컬럼 매칭 시작...")

        # 모든 고유 컬럼 수집
        all_columns = []
        for columns in columns_list:
            all_columns.extend(columns)
        unique_columns = list(set(all_columns))

        # 컬럼 그룹화
        column_groups = {}
        processed = set()

        for i, col1 in enumerate(unique_columns):
            if col1 in processed:
                continue

            group = [col1]
            processed.add(col1)

            # 나머지 컬럼들과 비교
            for col2 in unique_columns[i+1:]:
                if col2 in processed:
                    continue

                # AI로 유사도 계산
                result = self.calculate_semantic_similarity(
                    col1, col2,
                    context="엑셀 컬럼명 (학생/교사 정보)"
                )

                if result['is_similar']:
                    group.append(col2)
                    processed.add(col2)
                    print(f"  🔗 매칭: '{col1}' ↔ '{col2}' (유사도: {result['similarity']}%, {result['reason']})")

                # API 호출 제한 대비
                time.sleep(0.1)

            # 대표 컬럼명 선택 (AI 제안 또는 첫 번째)
            if len(group) > 1:
                # AI에게 최적의 컬럼명 제안 받기
                representative = self._select_best_column_name(group)
            else:
                representative = col1

            column_groups[representative] = group

        return column_groups

    def _select_best_column_name(self, column_names: List[str]) -> str:
        """
        여러 컬럼명 중 가장 적합한 것을 AI가 선택

        Args:
            column_names: 컬럼명 리스트

        Returns:
            선택된 컬럼명
        """
        if len(column_names) == 1:
            return column_names[0]

        prompt = f"""
다음 컬럼명들 중 가장 표준적이고 명확한 것을 하나 선택하세요:

{', '.join([f'"{name}"' for name in column_names])}

선택 기준:
1. 가장 명확하고 표준적인 표현
2. 한글 > 영어 (한국 데이터이므로)
3. 전체 표현 > 약어
4. 일반적으로 많이 사용되는 표현

**응답 형식**: 선택한 컬럼명만 출력 (따옴표 없이)
"""

        try:
            response = self.model.generate_content(prompt)
            selected = response.text.strip().strip('"\'')

            # 응답이 리스트에 있는지 확인
            if selected in column_names:
                return selected
            else:
                # AI 응답이 이상하면 첫 번째 선택
                return column_names[0]

        except Exception as e:
            print(f"⚠️  컬럼명 선택 실패: {str(e)}")
            return column_names[0]

    def match_values_smart(
        self,
        values: List[str],
        value_type: str = "일반"
    ) -> Dict[str, List[str]]:
        """
        값들을 AI로 분석하여 그룹화

        Args:
            values: 값 리스트
            value_type: 값 타입 (학교명, 이름, 주소 등)

        Returns:
            {대표값: [유사한 값들]}
        """
        unique_values = list(set([str(v) for v in values if v and str(v).strip()]))

        if len(unique_values) <= 1:
            return {unique_values[0]: unique_values} if unique_values else {}

        print(f"\n🤖 AI 기반 값 매칭 시작 (타입: {value_type})...")

        value_groups = {}
        processed = set()

        for i, val1 in enumerate(unique_values):
            if val1 in processed:
                continue

            group = [val1]
            processed.add(val1)

            for val2 in unique_values[i+1:]:
                if val2 in processed:
                    continue

                # AI로 유사도 계산
                result = self.calculate_semantic_similarity(
                    val1, val2,
                    context=f"{value_type} 값"
                )

                if result['is_similar']:
                    group.append(val2)
                    processed.add(val2)
                    print(f"  🔗 매칭: '{val1}' ↔ '{val2}' (유사도: {result['similarity']}%)")

                time.sleep(0.1)

            # 대표값: AI가 제안한 mapping 또는 가장 긴 값
            if len(group) > 1 and result.get('mapping'):
                representative = result['mapping']
            else:
                representative = max(group, key=len)

            value_groups[representative] = group

        return value_groups

    def verify_and_expand_school_name(
        self,
        school_name: str,
        gangwon_regions: Dict[str, str]
    ) -> Dict[str, str]:
        """
        AI를 사용하여 학교명 검증 및 확장
        중고등학교의 경우 풀네임 확인 후 강원도 교육청 자동 매칭

        Args:
            school_name: 학교명 (약칭 또는 풀네임)
            gangwon_regions: 강원도 지역명→교육청명 매핑 딕셔너리

        Returns:
            {
                'full_name': 풀네임 학교명,
                'education_office': 교육지원청명 (강원도 내 학교인 경우),
                'region': 지역명,
                'confidence': 신뢰도 (0-100),
                'explanation': 설명
            }
        """
        if not school_name or not school_name.strip():
            return {
                'full_name': school_name,
                'education_office': '',
                'region': '',
                'confidence': 0,
                'explanation': '빈 학교명'
            }

        cache_key = f"school_verify||{school_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 강원도 지역 목록 생성
        region_list = ', '.join(gangwon_regions.keys())

        prompt = f"""
당신은 강원도 교육청 전문가입니다. 학교명을 분석하여 다음 정보를 제공하세요.

**입력 학교명**: "{school_name}"

**강원도 지역 목록**: {region_list}

**작업**:
1. 학교명이 약칭인 경우 정식 명칭으로 확장하세요
   예: "춘천공고" → "춘천공업고등학교"
       "원주여고" → "원주여자고등학교"
       "강릉고" → "강릉고등학교"
       "삼척중" → "삼척중학교"

2. 학교가 강원도 내 학교인지 확인하고, 해당 지역을 찾으세요
   예: "춘천공업고등학교" → 춘천
       "원주여자고등학교" → 원주
       "강릉중앙초등학교" → 강릉

3. 신뢰도를 계산하세요 (0-100)
   - 강원도 내 실제 존재하는 학교: 90-100
   - 강원도 내 학교로 추정: 70-89
   - 강원도 외 지역 학교: 50-69
   - 불명확: 0-49

**응답 형식** (JSON):
{{
    "full_name": "정식 학교명 (확장된 풀네임)",
    "region": "지역명 (강원도 지역 목록 중 하나, 없으면 빈 문자열)",
    "confidence": 0-100 사이의 숫자,
    "explanation": "판단 근거 설명"
}}

JSON만 출력하세요.
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # JSON 파싱
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            result = json.loads(result_text)

            # 교육청명 추가
            region = result.get('region', '')
            education_office = ''
            if region and region in gangwon_regions:
                education_office = gangwon_regions[region]

            result['education_office'] = education_office

            # 캐시에 저장
            self.cache[cache_key] = result

            return result

        except Exception as e:
            print(f"⚠️  학교명 검증 실패 ({school_name}): {str(e)}")
            return {
                'full_name': school_name,
                'education_office': '',
                'region': '',
                'confidence': 0,
                'explanation': f'AI 분석 실패: {str(e)}'
            }


def test_gemini_matcher():
    """테스트 함수"""
    import os

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수를 설정하세요")
        return

    matcher = GeminiMatcher(api_key)

    # 테스트 1: 컬럼명 유사도
    print("=" * 70)
    print("테스트 1: 컬럼명 유사도")
    print("=" * 70)

    test_pairs = [
        ("이름", "성명"),
        ("학교", "대학교"),
        ("전공", "전공분야"),
        ("연락처", "전화번호"),
        ("email", "이메일"),
        ("HP", "휴대폰"),
    ]

    for col1, col2 in test_pairs:
        result = matcher.calculate_semantic_similarity(col1, col2)
        print(f"\n'{col1}' ↔ '{col2}'")
        print(f"  유사도: {result['similarity']}%")
        print(f"  유사함: {result['is_similar']}")
        print(f"  이유: {result['reason']}")
        print(f"  제안: {result['mapping']}")


if __name__ == '__main__':
    test_gemini_matcher()
