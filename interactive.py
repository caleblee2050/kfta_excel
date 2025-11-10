#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Unifier - 인터랙티브 모드
파일을 드래그 앤 드롭하거나 경로를 입력하여 사용할 수 있습니다.
"""

import sys
import os
from excel_unifier import ExcelUnifier


def main():
    print("=" * 70)
    print("📊 Excel Unifier - 인터랙티브 모드")
    print("=" * 70)
    print("\n여러 양식의 엑셀 파일을 자동으로 분석하고 통합합니다.\n")

    # 파일 경로 입력
    print("📁 통합할 엑셀 파일 경로를 입력하세요 (공백으로 구분):")
    print("   예: file1.xlsx file2.xlsx file3.xlsx")
    print("   또는 드래그 앤 드롭하세요\n")

    file_input = input("파일 경로: ").strip()

    if not file_input:
        print("❌ 파일 경로가 입력되지 않았습니다.")
        return

    # 경로를 공백으로 분리하고 따옴표 제거
    file_paths = []
    for path in file_input.split():
        path = path.strip().strip("'").strip('"')
        if os.path.exists(path):
            file_paths.append(path)
        else:
            print(f"⚠️  경고: 파일을 찾을 수 없습니다 - {path}")

    if not file_paths:
        print("❌ 유효한 파일이 없습니다.")
        return

    # 출력 파일명 입력
    print("\n💾 출력 파일명을 입력하세요 (기본값: unified_output.xlsx):")
    output_file = input("출력 파일명: ").strip()
    if not output_file:
        output_file = "unified_output.xlsx"

    # 키 컬럼 입력
    print("\n🔑 중복 제거에 사용할 키 컬럼을 입력하세요 (공백으로 구분, 선택사항):")
    print("   예: 이름 학교")
    print("   (Enter를 누르면 건너뜁니다)\n")
    key_cols_input = input("키 컬럼: ").strip()
    key_columns = key_cols_input.split() if key_cols_input else None

    # 유사도 임계값 입력
    print("\n📊 유사도 임계값을 입력하세요 (0-100, 기본값: 85):")
    print("   높을수록 엄격, 낮을수록 관대")
    threshold_input = input("임계값: ").strip()

    try:
        threshold = int(threshold_input) if threshold_input else 85
        if not 0 <= threshold <= 100:
            threshold = 85
            print(f"⚠️  범위를 벗어나 기본값 {threshold} 사용")
    except ValueError:
        threshold = 85
        print(f"⚠️  잘못된 입력, 기본값 {threshold} 사용")

    # 리포트 파일 생성 여부
    print("\n📋 분석 리포트를 생성하시겠습니까? (y/n, 기본값: n):")
    report_input = input("리포트 생성: ").strip().lower()
    report_file = None
    if report_input in ['y', 'yes', '예']:
        report_file = output_file.replace('.xlsx', '_report.txt')
        print(f"   → 리포트 파일: {report_file}")

    print("\n" + "=" * 70)
    print("🚀 처리 시작...")
    print("=" * 70)

    # Excel Unifier 실행
    try:
        unifier = ExcelUnifier(similarity_threshold=threshold)
        unifier.load_excel_files(file_paths)
        unifier.analyze_columns()

        unified_df = unifier.unify_dataframes(key_columns=key_columns)
        unifier.save_unified_excel(output_file, unified_df)

        if report_file:
            report = unifier.generate_report(report_file)
            print("\n" + report)

        print("\n" + "=" * 70)
        print("✅ 완료!")
        print("=" * 70)
        print(f"\n📄 결과 파일: {os.path.abspath(output_file)}")
        if report_file:
            print(f"📄 리포트 파일: {os.path.abspath(report_file)}")

        # 결과 미리보기
        print("\n📊 결과 미리보기 (처음 5행):")
        print(unified_df.head().to_string(index=False))

    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {str(e)}")
