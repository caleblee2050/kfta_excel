#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
유사도 알고리즘 데모 - 실제 계산 과정 보기
"""

from fuzzywuzzy import fuzz

print("=" * 70)
print("📊 Excel Unifier - 유사도 알고리즘 데모")
print("=" * 70)
print("\nLevenshtein Distance 기반 문자열 유사도 계산\n")

# 컬럼명 유사도 예시
print("1️⃣ 컬럼명 유사도 계산")
print("-" * 70)

column_pairs = [
    ("이름", "성명"),
    ("이름", "학생명"),
    ("이름", "이 름"),
    ("학교", "대학교"),
    ("학교", "소속대학"),
    ("전공", "전공분야"),
    ("연락처", "전화번호"),
    ("연락처", "휴대폰"),
]

threshold = 85
print(f"임계값: {threshold}\n")

for col1, col2 in column_pairs:
    similarity = fuzz.ratio(col1, col2)
    match = "✅ 매칭" if similarity >= threshold else "❌ 불일치"
    print(f"{col1:10s} ↔ {col2:10s} : {similarity:3d}% {match}")

# 값 유사도 예시
print("\n" + "=" * 70)
print("2️⃣ 학교명 유사도 계산")
print("-" * 70)

school_pairs = [
    ("서울대학교", "서울대"),
    ("서울대학교", "서울大學校"),
    ("연세대", "연세대학교"),
    ("고려대학교", "고려대"),
    ("한양대학교", "한양대"),
]

print(f"임계값: {threshold}\n")

for school1, school2 in school_pairs:
    similarity = fuzz.ratio(school1, school2)
    match = "✅ 매칭" if similarity >= threshold else "❌ 불일치"
    print(f"{school1:15s} ↔ {school2:15s} : {similarity:3d}% {match}")

# 정규화 후 비교
print("\n" + "=" * 70)
print("3️⃣ 정규화 후 학교명 비교")
print("-" * 70)

def normalize_school(value):
    """학교명 정규화"""
    replacements = [
        ('大學校', ''),
        ('大学校', ''),
        ('대학교', ''),
        ('대학', ''),
        (' ', ''),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    return value.lower()

print("정규화 규칙: 한자/접미사/공백 제거\n")

for school1, school2 in school_pairs:
    norm1 = normalize_school(school1)
    norm2 = normalize_school(school2)
    is_same = norm1 == norm2
    match = "✅ 동일" if is_same else "❌ 다름"
    print(f"{school1:15s} → {norm1:10s}")
    print(f"{school2:15s} → {norm2:10s}")
    print(f"결과: {match}\n")

# 다양한 임계값 테스트
print("=" * 70)
print("4️⃣ 임계값 변화에 따른 매칭 결과")
print("-" * 70)

test_pair = ("전공", "전공분야")
similarity = fuzz.ratio(test_pair[0], test_pair[1])

print(f"테스트 쌍: '{test_pair[0]}' ↔ '{test_pair[1]}'")
print(f"유사도: {similarity}%\n")

thresholds = [70, 75, 80, 85, 90, 95]
print("임계값별 매칭 결과:")
for t in thresholds:
    match = "✅ 매칭" if similarity >= t else "❌ 불일치"
    print(f"  임계값 {t:2d}%: {match}")

print("\n" + "=" * 70)
print("💡 결론")
print("=" * 70)
print("""
1. Levenshtein Distance 알고리즘 사용 (AI 불필요)
2. 0-100 사이의 유사도 점수 계산
3. 임계값(기본 85)보다 높으면 매칭
4. 정규화를 통해 다양한 표기 통일
5. 빠르고 정확하며 비용 무료!
""")
