#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KFTA 형식으로 파일 처리 테스트
"""

from excel_unifier import ExcelUnifier
import sys

def main(input_file, output_file):
    """KFTA 형식으로 파일 처리"""

    # ExcelUnifier 생성 (KFTA 형식)
    unifier = ExcelUnifier(similarity_threshold=85, use_ai=False)

    # 파일 로드
    unifier.load_excel_files([input_file])

    # 컬럼 분석
    unifier.analyze_columns()

    # 데이터 통합 (KFTA 형식으로)
    unified_df = unifier.unify_dataframes(output_format='kfta')

    # 결과 저장
    unifier.save_unified_excel(output_file, unified_df)

    # 처음 10행 출력
    print("\n📊 결과 데이터 미리보기 (처음 10행):")
    print(unified_df.head(10).to_string())

    print(f"\n✅ 완료! 결과 파일: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("사용법: python test_kfta_processing.py <입력파일> <출력파일>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
