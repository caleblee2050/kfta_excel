# KFTA Parser 개선사항

## 구현 완료 기능

### 1. 필드명 매핑 추가 ✅
**파일**: `excel_unifier.py`

- '현재분회' → '현재본청' 매핑 추가
- '발령분회' → '발령본청' 매핑 추가
- '이름', '성명' → '대응' 매핑 추가

**위치**: `excel_unifier.py:117-120`

```python
'현재본청': ['현재본청', '현재 본청', '현재학교', '현 본청', '현재 학교', '소속학교', '소속본청', '현재분회', '현재 분회'],
'대응': ['대응', '대 응', '이름', '성명'],
'발령본청': ['발령본청', '발령 본청', '전입학교', '배치학교', '발령학교', '발령 학교', '전보학교', '발령분회', '발령 분회'],
```

---

### 2. 학교명 약식 표기 파싱 ✅
**파일**: `kfta_parser.py`

**기능**: "□□ OO초" 형식 처리
- 지역명 추출 → 교육청 자동 매핑
- 학교명 약칭 → 풀네임 변환

**메서드**: `parse_abbreviated_school_format()`

**예시**:
- "춘천 남산초" → ("강원특별자치도춘천교육지원청", "남산초등학교")
- "원주중앙초" → ("강원특별자치도원주교육지원청", "중앙초등학교")

---

### 3. 학교 약칭 확장 매핑 ✅
**파일**: `kfta_parser.py`

**매핑 규칙** (`SCHOOL_ABBR_MAPPINGS`):
```python
'공고': '공업고등학교',
'정산고': '정보산업고등학교',
'산과고': '산업과학고등학교',
'여고': '여자고등학교',
'여중': '여자중학교',
'고': '고등학교',
'중': '중학교',
'초': '초등학교',
```

**메서드**: `expand_school_abbreviation()`

**예시**:
- "춘천공고" → "춘천공업고등학교"
- "원주정산고" → "원주정보산업고등학교"
- "속초여고" → "속초여자고등학교"
- "태백고" → "태백고등학교"

---

### 4. 직위명 정규화 ✅
**파일**: `kfta_parser.py`

**정규화 규칙** (`POSITION_NORMALIZATION`):
```python
'초등학교 교감' / '중등학교 교감' → '교감'
'초등학교 교사' / '중등학교 교사' → '교사'
'특수학교교사(초등)' / '특수학교교사(중등)' → '특수교사'
```

**메서드**: `normalize_position()`

**적용 위치**: `parse_row_to_kfta()` 메서드의 직위 필드 처리

---

### 5. AI 기반 학교명 검증 및 교육청 매칭 ✅
**파일**: `ai_matcher.py`, `kfta_parser.py`

#### ai_matcher.py 추가 메서드
**메서드**: `verify_and_expand_school_name()`

**기능**:
- 학교명 약칭 → 정식 명칭 확장
- 강원도 내 학교 판별
- 지역 자동 추출 → 교육청 매핑
- 신뢰도 점수 제공 (0-100)

**응답 형식**:
```python
{
    'full_name': '정식 학교명',
    'education_office': '강원특별자치도OO교육지원청',
    'region': '지역명',
    'confidence': 95,
    'explanation': '판단 근거'
}
```

#### kfta_parser.py 통합
**메서드**: `verify_and_expand_with_ai()`

- 중고등학교 학교명 자동 감지
- AI 검증 우선 시도
- 신뢰도 < 50%인 경우 기본 파서로 fallback
- 신뢰도 >= 70%인 경우 로그 출력

**활성화 방법**:
```python
# KFTAParser 초기화 시
parser = KFTAParser(use_ai=True, ai_matcher=ai_matcher)

# ExcelUnifier에서 자동 전달
unifier = ExcelUnifier(use_ai=True)
```

---

## 통합 워크플로우

### 기본 모드 (AI 미사용)
```
입력 데이터 → KFTA Parser
  ↓
1. 필드명 매핑
2. 약칭 확장 (규칙 기반)
3. 약식 표기 파싱 (패턴 매칭)
4. 직위명 정규화 (딕셔너리 기반)
  ↓
KFTA 12개 표준 컬럼 출력
```

### AI 모드 (use_ai=True)
```
입력 데이터 → KFTA Parser (AI enabled)
  ↓
1. 필드명 매핑
2. 중고등학교 감지
  ├─ 중고등학교 → AI 검증 우선
  │   ├─ 신뢰도 >= 70% → AI 결과 사용
  │   └─ 신뢰도 < 50% → 기본 파서로 fallback
  └─ 초등학교 → 기본 파서 사용
3. 약식 표기 파싱
4. 직위명 정규화
  ↓
KFTA 12개 표준 컬럼 출력
```

---

## 사용 예시

### CLI 사용
```bash
# 기본 모드
./run.sh input.xlsx -o output.xlsx --output-format kfta

# AI 모드 (중고등학교 풀네임 자동 확인)
./run.sh input.xlsx -o output.xlsx --ai --output-format kfta
```

### Python 코드 사용
```python
from excel_unifier import ExcelUnifier

# AI 모드로 초기화
unifier = ExcelUnifier(use_ai=True)

# 파일 로드
unifier.load_excel_files(['input.xlsx'])

# KFTA 형식으로 통합
unified_df = unifier.unify_dataframes(output_format='kfta')

# 저장
unifier.save_unified_excel('output.xlsx', unified_df)
```

---

## 테스트 결과

모든 기능이 정상 작동함을 확인:
- ✅ 학교 약칭 확장 (8개 테스트 케이스 통과)
- ✅ 약식 학교명 파싱 (4개 테스트 케이스 통과)
- ✅ 직위명 정규화 (13개 테스트 케이스 통과)
- ✅ 행 데이터 파싱 통합 (2개 테스트 케이스 통과)

**테스트 파일**: `test_kfta_enhancements.py`

**실행 명령**:
```bash
venv/bin/python test_kfta_enhancements.py
```

---

## 주의사항

### 동일 학교명 문제
다음 학교들은 여러 지역에 존재하여 추가 처리가 필요할 수 있음:

**초등학교**:
- 남산초등학교: 춘천, 홍천, 강릉
- 중앙초등학교: 춘천, 원주, 강릉, 동해
- 조양초등학교: 춘천, 속초

**해결 방안**:
1. 비고란에 시군 정보 확인
2. 관내 인사이동 여부 확인
3. AI 검증 시 추가 컨텍스트 제공

---

## 향후 개선 가능 사항

1. **동일 학교명 처리**: 비고란 또는 추가 필드를 참조하여 지역 확정
2. **학교명 데이터베이스**: 강원도 전체 학교 목록 DB 구축
3. **신뢰도 임계값 조정**: 사용자가 AI 신뢰도 임계값 설정 가능
4. **캐싱 개선**: AI 결과를 파일로 저장하여 재사용
5. **배치 처리 최적화**: 여러 학교명 동시 AI 검증

---

## 기술 스택

- **Python 3.7+**
- **pandas**: 데이터 처리
- **google-generativeai**: Gemini 2.5 Flash API
- **fuzzywuzzy**: 문자열 유사도 계산
- **python-dotenv**: 환경변수 관리

---

## 관련 파일

| 파일 | 역할 |
|------|------|
| `kfta_parser.py` | KFTA 표준 형식 파서 (핵심 로직) |
| `ai_matcher.py` | AI 기반 학교명 검증 |
| `excel_unifier.py` | 통합 엔진 (파서 호출) |
| `app.py` | 웹 UI (Streamlit) |
| `test_kfta_enhancements.py` | 기능 테스트 |

---

**작성일**: 2025-11-12
**버전**: 1.0
**상태**: ✅ 구현 완료 및 테스트 통과
