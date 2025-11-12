#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 파일 분석 스크립트
"""

import pandas as pd
import sys

def analyze_file(file_path):
    """엑셀 파일 구조 분석"""
    print(f"📁 파일 분석: {file_path}\n")

    try:
        # 모든 시트 읽기
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 발견된 시트: {excel_file.sheet_names}\n")

        for sheet_name in excel_file.sheet_names:
            print(f"\n{'='*60}")
            print(f"시트: {sheet_name}")
            print(f"{'='*60}")

            df = pd.read_excel(file_path, sheet_name=sheet_name)

            print(f"\n총 행 수: {len(df)}")
            print(f"총 컬럼 수: {len(df.columns)}")
            print(f"\n컬럼명:\n{list(df.columns)}")

            print(f"\n첫 10행 데이터:\n")
            print(df.head(10).to_string())

            print(f"\n데이터 타입:\n{df.dtypes}")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법: python test_file_analysis.py <파일경로>")
        sys.exit(1)

    analyze_file(sys.argv[1])
