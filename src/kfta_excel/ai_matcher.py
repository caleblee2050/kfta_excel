#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 유사도 매칭 모듈
Gemini API를 활용한 의미론적 유사도 분석
"""

import json
import os
import time
from functools import lru_cache
from typing import Dict, List, Optional

try:
    # New SDK (preferred)
    from google import genai as genai_sdk
except ImportError:  # pragma: no cover - optional dependency fallback
    genai_sdk = None

try:
    # Legacy SDK fallback
    import google.generativeai as legacy_genai
except ImportError:  # pragma: no cover - optional dependency fallback
    legacy_genai = None


class GeminiMatcher:
    """Gemini AI를 활용한 스마트 매칭"""

    DEFAULT_MODEL_CANDIDATES = (
        "gemini-3-flash",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API 키가 필요합니다. "
                "GEMINI_API_KEY 환경변수를 설정하거나 api_key 파라미터를 전달하세요."
            )

        self.model_candidates = self._build_model_candidates(model_name, fallback_models)
        self.active_model_name = self.model_candidates[0]
        self.backend = self._init_backend()
        print(f"🤖 Gemini 모델 활성화: {self.active_model_name} ({self.backend})")

        # 같은 요청 반복 호출 방지
        self.cache = {}

    def _init_backend(self) -> str:
        if genai_sdk is not None:
            self.client = genai_sdk.Client(api_key=self.api_key)
            return "google.genai"

        if legacy_genai is not None:
            legacy_genai.configure(api_key=self.api_key)
            self.client = legacy_genai.GenerativeModel(self.active_model_name)
            return "google.generativeai"

        raise ImportError(
            "Gemini SDK를 찾을 수 없습니다. "
            "google-genai 또는 google-generativeai 패키지를 설치하세요."
        )

    @classmethod
    def _build_model_candidates(
        cls,
        model_name: Optional[str],
        fallback_models: Optional[List[str]],
    ) -> List[str]:
        env_model = os.getenv("GEMINI_MODEL", "").strip()
        primary = (model_name or env_model or cls.DEFAULT_MODEL_CANDIDATES[0]).strip()

        candidates = [primary]
        if fallback_models:
            candidates.extend([m.strip() for m in fallback_models if m and m.strip()])
        candidates.extend(cls.DEFAULT_MODEL_CANDIDATES)
        if env_model:
            candidates.append(env_model)

        deduped = []
        seen = set()
        for name in candidates:
            if name and name not in seen:
                deduped.append(name)
                seen.add(name)
        return deduped

    @staticmethod
    def _is_retryable_model_error(error: Exception) -> bool:
        message = str(error).lower()
        retryable_keywords = (
            "404",
            "not found",
            "unsupported",
            "invalid model",
            "resource has been exhausted",
            "quota",
            "permission denied",
        )
        return any(keyword in message for keyword in retryable_keywords)

    def _switch_model(self, model_name: str) -> None:
        self.active_model_name = model_name
        if self.backend == "google.generativeai":
            self.client = legacy_genai.GenerativeModel(model_name)
        print(f"🔁 Gemini 모델 전환: {model_name}")

    @staticmethod
    def _extract_text_from_new_sdk_response(response) -> str:
        text = getattr(response, "text", None)
        if text:
            return text

        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            if not content:
                continue
            parts = getattr(content, "parts", None) or []
            chunks = [getattr(part, "text", "") for part in parts if getattr(part, "text", "")]
            if chunks:
                return "\n".join(chunks)

        return str(response)

    def _generate_content(self, prompt: str) -> str:
        last_error = None
        tried = set()
        ordered_candidates = [self.active_model_name] + self.model_candidates

        for model_name in ordered_candidates:
            if model_name in tried:
                continue
            tried.add(model_name)

            try:
                if model_name != self.active_model_name:
                    self._switch_model(model_name)

                if self.backend == "google.genai":
                    response = self.client.models.generate_content(
                        model=self.active_model_name,
                        contents=prompt,
                    )
                    return self._extract_text_from_new_sdk_response(response)

                response = self.client.generate_content(prompt)
                return response.text
            except Exception as error:
                last_error = error
                if not self._is_retryable_model_error(error):
                    break
                print(f"⚠️ 모델 '{model_name}' 호출 실패, 다음 모델로 폴백: {error}")

        tried_models = ", ".join(ordered_candidates)
        raise RuntimeError(
            f"Gemini 모델 호출 실패 (시도: {tried_models}): {last_error}"
        ) from last_error

    @staticmethod
    def _strip_json_block(text: str) -> str:
        result_text = text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        return result_text.strip()

    @lru_cache(maxsize=1000)
    def calculate_semantic_similarity(
        self,
        text1: str,
        text2: str,
        context: str = "엑셀 컬럼명",
    ) -> Dict[str, any]:
        cache_key = f"{text1}||{text2}||{context}"
        if cache_key in self.cache:
            return self.cache[cache_key]

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
            raw = self._generate_content(prompt)
            result = json.loads(self._strip_json_block(raw))
            self.cache[cache_key] = result
            return result
        except Exception as error:
            print(f"⚠️  AI 분석 실패 ({text1} ↔ {text2}): {error}")
            return {
                "similarity": 0,
                "is_similar": False,
                "reason": f"AI 분석 실패: {error}",
                "mapping": text1,
            }

    def match_columns_batch(self, columns_list: List[List[str]]) -> Dict[str, List[str]]:
        print("\n🤖 AI 기반 컬럼 매칭 시작...")

        all_columns = []
        for columns in columns_list:
            all_columns.extend(columns)
        unique_columns = list(set(all_columns))

        column_groups = {}
        processed = set()

        for i, col1 in enumerate(unique_columns):
            if col1 in processed:
                continue

            group = [col1]
            processed.add(col1)

            for col2 in unique_columns[i + 1:]:
                if col2 in processed:
                    continue

                result = self.calculate_semantic_similarity(
                    col1,
                    col2,
                    context="엑셀 컬럼명 (학생/교사 정보)",
                )
                if result["is_similar"]:
                    group.append(col2)
                    processed.add(col2)
                    print(
                        f"  🔗 매칭: '{col1}' ↔ '{col2}' "
                        f"(유사도: {result['similarity']}%, {result['reason']})"
                    )
                time.sleep(0.1)

            representative = self._select_best_column_name(group) if len(group) > 1 else col1
            column_groups[representative] = group

        return column_groups

    def _select_best_column_name(self, column_names: List[str]) -> str:
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
            selected = self._generate_content(prompt).strip().strip("\"'")
            return selected if selected in column_names else column_names[0]
        except Exception as error:
            print(f"⚠️  컬럼명 선택 실패: {error}")
            return column_names[0]

    def match_values_smart(
        self,
        values: List[str],
        value_type: str = "일반",
    ) -> Dict[str, List[str]]:
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
            representative_suggestion = None

            for val2 in unique_values[i + 1:]:
                if val2 in processed:
                    continue

                result = self.calculate_semantic_similarity(
                    val1,
                    val2,
                    context=f"{value_type} 값",
                )

                if result["is_similar"]:
                    group.append(val2)
                    processed.add(val2)
                    if result.get("mapping"):
                        representative_suggestion = result["mapping"]
                    print(f"  🔗 매칭: '{val1}' ↔ '{val2}' (유사도: {result['similarity']}%)")

                time.sleep(0.1)

            representative = representative_suggestion if len(group) > 1 and representative_suggestion else max(group, key=len)
            value_groups[representative] = group

        return value_groups

    def verify_and_expand_school_name(
        self,
        school_name: str,
        gangwon_regions: Dict[str, str],
    ) -> Dict[str, str]:
        if not school_name or not school_name.strip():
            return {
                "full_name": school_name,
                "education_office": "",
                "region": "",
                "confidence": 0,
                "explanation": "빈 학교명",
            }

        cache_key = f"school_verify||{school_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        region_list = ", ".join(gangwon_regions.keys())
        prompt = f"""
당신은 강원도 교육청 전문가입니다. 학교명을 분석하여 다음 정보를 제공하세요.

**입력 학교명**: "{school_name}"
**강원도 지역 목록**: {region_list}

작업:
1. 약칭이면 정식 명칭으로 확장
2. 강원도 내 학교 여부와 지역 판별
3. confidence 0-100 산정

응답 형식(JSON):
{{
    "full_name": "정식 학교명",
    "region": "지역명",
    "confidence": 0,
    "explanation": "판단 근거"
}}
"""
        try:
            raw = self._generate_content(prompt)
            result = json.loads(self._strip_json_block(raw))
            region = result.get("region", "")
            result["education_office"] = gangwon_regions.get(region, "") if region else ""
            self.cache[cache_key] = result
            return result
        except Exception as error:
            print(f"⚠️  학교명 검증 실패 ({school_name}): {error}")
            return {
                "full_name": school_name,
                "education_office": "",
                "region": "",
                "confidence": 0,
                "explanation": f"AI 분석 실패: {error}",
            }


def test_gemini_matcher():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수를 설정하세요")
        return

    matcher = GeminiMatcher(api_key)
    test_pairs = [("이름", "성명"), ("학교", "대학교"), ("전공", "전공분야")]
    for col1, col2 in test_pairs:
        result = matcher.calculate_semantic_similarity(col1, col2)
        print(col1, col2, result)


if __name__ == "__main__":
    test_gemini_matcher()
