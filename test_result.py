#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""결과 파일 확인"""

import pandas as pd

print("=" * 70)
print("통합 결과 확인")
print("=" * 70)

# 통합 결과 읽기
df = pd.read_excel('examples/unified_result.xlsx')

print(f"\n총 {len(df)}개의 고유한 학생 데이터")
print(f"컬럼: {list(df.columns)}")
print("\n통합된 데이터:")
print(df.to_string(index=False))

print("\n" + "=" * 70)
print("원본 파일 비교")
print("=" * 70)

for filename in ['students_format_a.xlsx', 'students_format_b.xlsx', 'students_format_c.xlsx']:
    df_orig = pd.read_excel(f'examples/{filename}')
    print(f"\n{filename}:")
    print(f"  행 수: {len(df_orig)}")
    print(f"  컬럼: {list(df_orig.columns)}")
