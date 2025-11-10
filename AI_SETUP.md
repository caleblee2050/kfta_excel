# AI 모드 설정 가이드

Excel Unifier는 Gemini API를 활용한 AI 기반 유사도 매칭을 지원합니다.

## 🔑 Gemini API 키 발급

1. Google AI Studio 접속: https://makersuite.google.com/app/apikey
2. "Create API Key" 클릭
3. API 키 복사

## ⚙️ API 키 설정 방법

### 방법 1: 환경변수 사용 (권장)

1. `.env` 파일 생성:
```bash
cp .env.example .env
```

2. `.env` 파일 편집:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 방법 2: 명령줄 파라미터

```bash
./run.sh examples/*.xlsx -o output.xlsx --ai --api-key YOUR_API_KEY
```

### 방법 3: Python 코드에서 직접

```python
from excel_unifier import ExcelUnifier

unifier = ExcelUnifier(
    use_ai=True,
    gemini_api_key="YOUR_API_KEY"
)
```

## 🚀 AI 모드 사용법

### 명령줄

```bash
# AI 모드 활성화
./run.sh examples/*.xlsx -o output.xlsx --ai -k 이름 학교

# API 키 직접 지정
./run.sh examples/*.xlsx -o output.xlsx --ai --api-key YOUR_KEY
```

### Python 코드

```python
from excel_unifier import ExcelUnifier
import os

# 환경변수에서 API 키 읽기
unifier = ExcelUnifier(use_ai=True)

# 또는 직접 지정
unifier = ExcelUnifier(
    use_ai=True,
    gemini_api_key="YOUR_API_KEY"
)

unifier.load_excel_files(['file1.xlsx', 'file2.xlsx'])
unifier.analyze_columns()  # AI가 자동으로 컬럼 매칭
unified_df = unifier.unify_dataframes(key_columns=['이름', '학교'])
unifier.save_unified_excel('output.xlsx', unified_df)
```

## 🤖 AI 모드 vs 기본 모드

### 기본 모드 (Levenshtein Distance)

**장점:**
- 빠른 처리 속도
- API 키 불필요
- 오프라인 작동
- 무료

**한계:**
- "이름" ↔ "성명" 매칭 못함 (키워드 사전 필요)
- "email" ↔ "이메일" 다국어 매칭 못함
- 의미론적 유사도 이해 불가

**유사도 예시:**
```
"이름" ↔ "성명": 0% (매칭 실패)
"학교" ↔ "대학교": 80% (임계값 85 미만, 실패)
"전공" ↔ "전공분야": 67% (매칭 실패)
```

### AI 모드 (Gemini API)

**장점:**
- 의미론적 유사도 이해
- 다국어 매칭 가능
- 동의어 자동 인식
- 컨텍스트 이해
- 설명 제공

**한계:**
- API 호출 비용 발생
- 인터넷 연결 필요
- 처리 속도 느림 (API 호출 시간)

**유사도 예시:**
```
"이름" ↔ "성명": 95% ✅ (동의어 인식)
"학교" ↔ "대학교": 90% ✅ (의미 동일)
"전공" ↔ "전공분야": 85% ✅ (유사 개념)
"email" ↔ "이메일": 100% ✅ (다국어 매칭)
"HP" ↔ "휴대폰": 90% ✅ (약어 인식)
```

## 📊 하이브리드 매칭 시스템

Excel Unifier는 두 가지 방식을 결합한 **3단계 매칭**을 사용합니다:

```
1단계: 키워드 사전 매칭 (빠르고 정확)
   ↓ 실패 시
2단계: AI 유사도 분석 (AI 모드만)
   ↓ 실패 시
3단계: Levenshtein Distance (fallback)
```

이를 통해 **속도와 정확도를 모두** 확보합니다!

## 💰 비용 안내

### Gemini API 가격 (2024년 기준)

| 모델 | 무료 할당량 | 유료 가격 |
|------|------------|----------|
| Gemini Pro | 60 요청/분 | $0.00025 / 1K 문자 |

**예상 비용:**
- 100개 컬럼 매칭: 약 $0.01-0.02
- 1000개 값 매칭: 약 $0.10-0.20

대부분의 사용은 **무료 할당량 내**에서 가능합니다.

## 🔐 보안

- API 키는 `.env` 파일에 저장 (Git에 커밋 금지)
- `.gitignore`에 `.env` 추가됨
- 환경변수로 관리하여 코드에 노출 방지

## 🐛 문제 해결

### API 키 오류
```
ValueError: Gemini API 키가 필요합니다
```
**해결:** `.env` 파일에 `GEMINI_API_KEY` 설정

### 할당량 초과
```
ResourceExhausted: Quota exceeded
```
**해결:** 무료 할당량 초과. 1분 대기 또는 유료 플랜 전환

### 네트워크 오류
```
ConnectionError: Failed to connect
```
**해결:** 인터넷 연결 확인

### AI 모드 자동 비활성화
```
⚠️  AI 모드 초기화 실패. 기본 모드로 전환합니다.
```
**해결:** API 키 확인, 패키지 설치 확인
```bash
venv/bin/pip install google-generativeai
```

## 📚 추가 자료

- Gemini API 문서: https://ai.google.dev/docs
- API 키 관리: https://makersuite.google.com/app/apikey
- 가격 정보: https://ai.google.dev/pricing
