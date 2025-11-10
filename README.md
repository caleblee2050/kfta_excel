# Excel Unifier

통일되지 않은 양식으로 작성된 여러 엑셀 파일을 분석하여 자동으로 통합하는 도구입니다.

## 주요 기능

- **자동 컬럼 매핑**: 다른 이름을 사용하지만 유사한 의미의 컬럼을 자동으로 매칭
  - 예: "이름", "성명", "학생명" → "이름"으로 통일
  - 예: "학교", "대학교", "소속대학" → "학교"로 통일

- **유사값 통합**: 같은 내용이지만 표기가 다른 값들을 통합
  - 예: "서울대학교", "서울대", "서울大學校" → 동일한 것으로 인식
  - 예: "연세대", "연세대학교" → 통일

- **스마트 중복 제거**: 지정된 키 컬럼을 기준으로 중복 데이터 자동 병합
  - 이름과 학교가 같으면 하나의 레코드로 통합

- **통일된 양식 출력**: 모든 데이터를 하나의 통일된 형식의 엑셀 파일로 저장

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 기본 사용

```bash
# 실행 스크립트 사용 (권장)
./run.sh file1.xlsx file2.xlsx file3.xlsx -o output.xlsx

# 또는 직접 Python 실행
python excel_unifier.py file1.xlsx file2.xlsx file3.xlsx -o output.xlsx
```

### 키 컬럼 지정하여 중복 제거

```bash
./run.sh file1.xlsx file2.xlsx -o output.xlsx -k 이름 학교
```

이 경우 "이름"과 "학교" 값이 동일하거나 매우 유사한 행들을 하나로 통합합니다.

### 유사도 임계값 조정

```bash
./run.sh file1.xlsx file2.xlsx -o output.xlsx -t 90
```

- `-t` 또는 `--threshold`: 0-100 사이의 값 (기본값: 85)
- 높을수록 더 정확하게 일치해야 같은 것으로 인식
- 낮을수록 더 많은 항목을 유사한 것으로 간주

### 분석 리포트 생성

```bash
./run.sh file1.xlsx file2.xlsx -o output.xlsx -r report.txt
```

## 예제 실행

테스트용 예제 파일을 생성하고 실행해보세요:

```bash
# 1. 예제 파일 생성 (venv/bin/python 또는 python3 사용)
venv/bin/python example_generator.py

# 2. 통합 실행
./run.sh examples/*.xlsx -o examples/unified_result.xlsx -k 이름 학교

# 3. 결과 확인
# examples/unified_result.xlsx 파일이 생성됩니다
```

**예제 파일 설명:**
- `students_format_a.xlsx`: "이름", "학교", "전공" 등의 컬럼 사용
- `students_format_b.xlsx`: "성명", "대학교", "전공분야" 등의 컬럼 사용
- `students_format_c.xlsx`: "학생명", "소속대학", "전공" 등의 컬럼 사용
- 일부 학생 데이터가 중복되어 있으며, "서울대학교" vs "서울大學校" 같은 다른 표기 사용

## 명령줄 옵션

```
positional arguments:
  files                 통합할 엑셀 파일 경로들

optional arguments:
  -h, --help            도움말 표시
  -o OUTPUT, --output OUTPUT
                        출력 파일명 (기본값: unified_output.xlsx)
  -k KEY_COLUMNS [KEY_COLUMNS ...], --key-columns KEY_COLUMNS [KEY_COLUMNS ...]
                        중복 판단에 사용할 키 컬럼명들
  -t THRESHOLD, --threshold THRESHOLD
                        유사도 임계값 0-100 (기본값: 85)
  -r REPORT, --report REPORT
                        분석 리포트 저장 경로
```

## Python 모듈로 사용

```python
from excel_unifier import ExcelUnifier

# 초기화
unifier = ExcelUnifier(similarity_threshold=85)

# 파일 로드
unifier.load_excel_files([
    'file1.xlsx',
    'file2.xlsx',
    'file3.xlsx'
])

# 컬럼 분석
column_mappings = unifier.analyze_columns()

# 데이터 통합
unified_df = unifier.unify_dataframes(key_columns=['이름', '학교'])

# 결과 저장
unifier.save_unified_excel('output.xlsx', unified_df)

# 리포트 생성
report = unifier.generate_report('report.txt')
print(report)
```

## 작동 원리

1. **파일 로드**: 모든 엑셀 파일을 읽어들임 (.xlsx, .xls, .csv 지원)

2. **컬럼 분석**:
   - 모든 파일의 컬럼명을 수집
   - Levenshtein 거리 기반으로 유사한 컬럼명 그룹화
   - 가장 빈번한 컬럼명을 대표 컬럼명으로 선택

3. **데이터 통합**:
   - 각 파일의 컬럼을 통일된 컬럼명으로 매핑
   - 누락된 컬럼은 빈 값으로 채움
   - 모든 데이터를 하나의 데이터프레임으로 결합

4. **중복 제거** (키 컬럼 지정 시):
   - 값 정규화 (공백 제거, 대소문자 통일 등)
   - 유사도 기반으로 중복 탐지
   - 첫 번째 행 유지 (가장 완전한 데이터)

5. **결과 출력**: 통일된 형식의 엑셀 파일로 저장

## 지원 파일 형식

- `.xlsx` (Excel 2007 이상)
- `.xls` (Excel 97-2003)
- `.csv` (쉼표로 구분된 값)

## 요구사항

- Python 3.7 이상
- pandas
- openpyxl
- python-Levenshtein
- fuzzywuzzy

## 라이선스

MIT License

## 기여

이슈와 풀 리퀘스트를 환영합니다!
