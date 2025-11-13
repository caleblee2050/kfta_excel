#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Unifier - 웹 대시보드
Streamlit 기반 사용자 친화적 UI
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from excel_unifier import ExcelUnifier
import io
import tempfile
import os
from datetime import datetime

# 버전 정보
__version__ = "1.2.1"
__release_date__ = "2025-11-13"


# 페이지 설정
st.set_page_config(
    page_title="Excel Unifier",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    # 헤더
    st.markdown('<div class="main-header">📊 강원교총 엑셀통합 에이전트</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">여러 양식의 엑셀 파일을 자동으로 분석하고 통합하는 스마트 도구</div>',
        unsafe_allow_html=True
    )

    # 버전 정보 표시
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        st.caption(f"버전 {__version__} ({__release_date__})")

    # 세션 상태 초기화
    if 'unifier' not in st.session_state:
        st.session_state.unifier = None
    if 'unified_df' not in st.session_state:
        st.session_state.unified_df = None
    if 'uploaded_files_data' not in st.session_state:
        st.session_state.uploaded_files_data = []

    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 설정")

        # AI 모드 토글
        use_ai = st.checkbox(
            "🤖 AI 모드 (Gemini API)",
            value=True,
            help="AI를 활용하여 의미론적 유사도 분석 (동의어, 다국어, 약어 인식)"
        )

        if use_ai:
            st.info("✨ AI 모드: 동의어 및 다국어 매칭 지원")
            # API 키 확인
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                st.warning("⚠️ .env 파일에 GEMINI_API_KEY를 설정하세요")
            else:
                st.success("✅ API 키 확인됨")

        # 유사도 임계값
        threshold = st.slider(
            "유사도 임계값",
            min_value=0,
            max_value=100,
            value=85,
            help="높을수록 엄격하게 매칭, 낮을수록 관대하게 매칭"
        )

        # 출력 형식 선택
        st.subheader("📄 출력 형식")

        # 라벨과 실제 값 매핑
        format_labels = {
            "📋 KFTA 표준 (권장)": "kfta",
            "🔍 자동 감지": "auto",
            "📊 일반 형식": "standard"
        }

        selected_label = st.radio(
            "출력 형식을 선택하세요",
            options=list(format_labels.keys()),
            index=0,
            help="강원교총 표준 형식(KFTA)을 권장합니다",
            horizontal=False
        )

        # 실제 값으로 변환
        output_format = format_labels[selected_label]

        # 선택된 형식에 대한 상세 설명
        format_descriptions = {
            "kfta": """
**📋 KFTA 표준 형식 (강원교총 표준)**

✅ **12개 표준 컬럼**으로 구성:
- `현재교육청` - 현재 소속 교육지원청
- `현재분회` - 현재 소속 학교/기관
- `이름` - 성명
- `발령교육청` - 발령받은 교육지원청
- `발령분회` - 발령받은 학교/기관
- `과목` - 담당 과목 (중등)
- `직위` - 교사/교감/교장/원감 등
- `직종분류` - 교원 구분
- `분류명` - 세부 분류
- `취급코드` - 인사 코드
- `시군구분` - 지역 구분
- `교호기호등` - 학교 고유 기호

💡 **자동 처리 기능**:
- ✅ 중복 학교명 자동 해결 (원당초, 신동초, 교동초 등)
- ✅ 유치원 신규원감 비고란 파싱
- ✅ 학교 약칭 자동 확장 (OO초 → OO초등학교)
- ✅ 교육지원청 자동 매칭
            """,
            "auto": """
**🔍 자동 감지 형식**

입력 파일의 컬럼을 자동으로 분석하여 적절한 형식을 결정합니다.

- KFTA 컬럼이 감지되면 → KFTA 표준 형식 적용
- 일반 컬럼만 있으면 → 일반 형식 유지
            """,
            "standard": """
**📊 일반 형식**

모든 입력 컬럼을 병합하지 않고 그대로 유지합니다.

- 모든 원본 컬럼 포함
- 컬럼명만 통일 (유사한 이름 자동 매칭)
- KFTA 표준 변환 없음
            """
        }

        with st.expander("ℹ️ 선택한 형식 상세 정보", expanded=True):
            st.markdown(format_descriptions[output_format])

        st.divider()

        # 도움말
        with st.expander("ℹ️ 사용 방법"):
            st.markdown("""
            1. **파일 업로드**: 여러 엑셀 파일을 선택하세요
            2. **컬럼 확인**: 업로드된 파일의 컬럼을 확인하세요
            3. **키 컬럼 선택**: 중복 제거에 사용할 컬럼을 선택하세요
            4. **통합 실행**: 분석 및 통합을 시작하세요
            5. **결과 다운로드**: 통합된 파일을 다운로드하세요
            """)

        with st.expander("✨ 주요 기능"):
            st.markdown("""
            - **자동 컬럼 매핑**: 유사한 컬럼명 자동 통일
            - **스마트 값 정규화**: 표기가 다른 값 동일하게 인식
            - **지능형 중복 제거**: 키 컬럼 기반 중복 자동 병합
            - **실시간 미리보기**: 결과를 즉시 확인
            - **AI 모드**: 동의어, 다국어, 약어 자동 인식
            """)

        with st.expander("🤖 AI 모드 설명"):
            st.markdown("""
            **기본 모드 vs AI 모드:**

            | 항목 | 기본 모드 | AI 모드 |
            |-----|---------|---------|
            | "이름" ↔ "성명" | ❌ 0% | ✅ 95% |
            | "email" ↔ "이메일" | ❌ 0% | ✅ 100% |
            | "HP" ↔ "휴대폰" | ❌ 0% | ✅ 98% |
            | "학교" ↔ "대학교" | ⚠️ 80% | ✅ 90% |

            AI 모드는 Gemini API를 사용하여 의미론적 유사도를 분석합니다.
            .env 파일에 GEMINI_API_KEY 설정이 필요합니다.
            """)

    # 메인 영역
    tab1, tab2, tab3, tab4 = st.tabs(["📁 파일 업로드", "🔍 데이터 분석", "📊 결과 확인", "📈 통계"])

    # Tab 1: 파일 업로드
    with tab1:
        st.header("파일 업로드")

        uploaded_files = st.file_uploader(
            "엑셀 파일을 선택하세요 (.xlsx, .xls, .csv)",
            type=['xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            help="여러 파일을 동시에 선택할 수 있습니다"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)}개 파일이 업로드되었습니다!")

            # 파일 정보 표시
            file_info = []
            st.session_state.uploaded_files_data = []

            for i, file in enumerate(uploaded_files):
                # 임시 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
                    tmp.write(file.getvalue())
                    tmp_path = tmp.name

                st.session_state.uploaded_files_data.append({
                    'name': file.name,
                    'path': tmp_path,
                    'size': file.size
                })

                # 파일 미리보기
                try:
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(tmp_path)
                        file_info.append({
                            '파일명': file.name,
                            '시트': '-',
                            '행 수': len(df),
                            '컬럼 수': len(df.columns),
                            '크기': f"{file.size / 1024:.1f} KB"
                        })

                        with st.expander(f"📄 {file.name} 미리보기"):
                            st.dataframe(df.head(5), use_container_width=True)
                            st.caption(f"컬럼: {', '.join(df.columns.tolist())}")
                    else:
                        # 엑셀 파일의 모든 시트 읽기
                        excel_file = pd.ExcelFile(tmp_path)
                        sheet_names = excel_file.sheet_names

                        with st.expander(f"📄 {file.name} 미리보기 ({len(sheet_names)}개 시트)"):
                            for sheet_name in sheet_names:
                                df = pd.read_excel(tmp_path, sheet_name=sheet_name)

                                # 빈 시트 건너뛰기
                                if df.empty or len(df.columns) == 0:
                                    st.caption(f"⊘ 시트 '{sheet_name}': 빈 시트")
                                    continue

                                file_info.append({
                                    '파일명': file.name,
                                    '시트': sheet_name,
                                    '행 수': len(df),
                                    '컬럼 수': len(df.columns),
                                    '크기': f"{file.size / 1024:.1f} KB"
                                })

                                st.markdown(f"**시트: {sheet_name}**")
                                st.dataframe(df.head(5), use_container_width=True)
                                st.caption(f"컬럼: {', '.join(df.columns.tolist())}")
                                st.divider()

                except Exception as e:
                    st.error(f"❌ {file.name} 읽기 실패: {str(e)}")

            # 파일 정보 요약 테이블
            if file_info:
                st.subheader("업로드된 파일 요약")
                st.dataframe(pd.DataFrame(file_info), use_container_width=True)

    # Tab 2: 데이터 분석
    with tab2:
        st.header("데이터 분석 및 통합")

        if not st.session_state.uploaded_files_data:
            st.info("👈 먼저 파일을 업로드해주세요")
        else:
            # 키 컬럼 선택
            st.subheader("🔑 중복 제거 설정")

            # 상세 설명 추가
            with st.expander("❓ 중복 제거 설정이란?", expanded=False):
                st.markdown("""
                ### 중복 제거 설정의 역할

                여러 엑셀 파일을 통합할 때, **같은 사람의 정보가 여러 파일에 중복**되어 있을 수 있습니다.
                중복 제거 설정은 이런 중복 데이터를 자동으로 찾아서 하나로 병합하는 기능입니다.

                ---

                #### 🎯 언제 필요한가요?

                **필요한 경우:**
                - 같은 명단이 여러 파일에 나눠져 있을 때
                - 정기 업데이트된 파일들을 합칠 때
                - 중복된 인원 정보를 정리하고 싶을 때

                **예시:**
                - `2024년_명단.xlsx`와 `2025년_명단.xlsx`를 합치는데,
                  2024년에 있던 김철수 선생님이 2025년에도 있다면 → **중복!**

                **불필요한 경우:**
                - 완전히 다른 학교의 명단을 합칠 때
                - 모든 행이 고유한 경우

                ---

                #### 🔑 키 컬럼이란?

                **키 컬럼**: 중복을 판단하는 기준이 되는 컬럼입니다.

                **선택 방법:**
                1. **개인 식별용**: `이름`, `이름+학교`, `이름+생년월일` 등
                2. **조직 식별용**: `학교명`, `부서명` 등

                **예시:**
                - 키 컬럼 = `[이름, 학교]` 선택 시:
                  ```
                  파일1: 김철수, 춘천고등학교, 010-1234-5678
                  파일2: 김철수, 춘천고등학교, 010-9999-9999
                  → 같은 사람으로 판단 → 하나로 병합 (최신 정보 우선)
                  ```

                - 키 컬럼 = `[이름]`만 선택 시:
                  ```
                  파일1: 김철수, 춘천고등학교
                  파일2: 김철수, 원주고등학교
                  → 같은 사람으로 판단 (학교가 달라도!)
                  ```

                ---

                #### ⚙️ 동작 원리

                1. **정규화**: 공백 제거, 대소문자 통일
                   - "김 철수" → "김철수"
                   - "춘천 고등학교" → "춘천고등학교"

                2. **중복 판단**: 키 컬럼의 값이 모두 같으면 중복
                   - 키 컬럼 = [이름, 학교]
                   - 행1: 이름=김철수, 학교=춘천고
                   - 행2: 이름=김철수, 학교=춘천고
                   - → **중복!** (두 키가 모두 같음)

                3. **병합**: 중복된 행 중 가장 나중 파일의 정보를 사용

                ---

                #### 💡 권장 설정

                | 상황 | 권장 키 컬럼 | 설명 |
                |-----|------------|------|
                | 교직원 명단 통합 | `이름`, `학교` | 같은 학교의 같은 이름만 중복 처리 |
                | 개인 정보 통합 | `이름`, `생년월일` | 동명이인 구분 |
                | 학교 정보 통합 | `학교명` | 학교 단위 중복 제거 |
                | 중복 제거 안 함 | 비워두기 | 모든 행 유지 |

                ---

                #### ⚠️ 주의사항

                - **키 컬럼을 선택하지 않으면**: 중복 제거를 하지 않습니다 (모든 행 유지)
                - **너무 적은 키 컬럼**: 다른 사람도 같은 사람으로 인식될 수 있음
                  - 예: `이름`만 선택 → 모든 "김철수"가 같은 사람으로 처리
                - **너무 많은 키 컬럼**: 중복 제거가 잘 안 될 수 있음
                  - 예: 모든 컬럼 선택 → 하나라도 다르면 다른 사람으로 인식
                """)

            col1, col2 = st.columns([2, 1])

            with col1:
                # 모든 컬럼 수집
                all_columns = set()
                for file_data in st.session_state.uploaded_files_data:
                    try:
                        if file_data['name'].endswith('.csv'):
                            df = pd.read_csv(file_data['path'])
                        else:
                            df = pd.read_excel(file_data['path'])
                        all_columns.update(df.columns.tolist())
                    except:
                        pass

                key_columns = st.multiselect(
                    "키 컬럼 선택 (중복 판단 기준)",
                    options=sorted(list(all_columns)),
                    default=[],
                    help="예: 이름, 학교 등을 선택하면 같은 이름+학교 조합은 중복으로 판단됩니다. 비워두면 중복 제거를 하지 않습니다."
                )

                # 도움말 표시
                if not key_columns:
                    st.info("💡 키 컬럼을 선택하지 않으면 중복 제거를 하지 않습니다 (모든 행 유지)")
                else:
                    st.success(f"✅ 선택된 키: {', '.join(key_columns)}\n\n이 컬럼들의 값이 모두 같으면 중복으로 판단합니다.")

            with col2:
                st.metric("선택된 키 컬럼", len(key_columns))
                st.metric("유사도 임계값", f"{threshold}%")

            # 통합 실행 버튼
            st.divider()

            if st.button("🚀 분석 및 통합 실행", type="primary", use_container_width=True):
                with st.spinner("분석 중... 잠시만 기다려주세요"):
                    try:
                        # ExcelUnifier 실행 (AI 모드 포함)
                        unifier = ExcelUnifier(
                            similarity_threshold=threshold,
                            use_ai=use_ai
                        )
                        file_paths = [f['path'] for f in st.session_state.uploaded_files_data]

                        # 진행 상황 표시
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        status_text.text("📂 파일 로드 중...")
                        unifier.load_excel_files(file_paths)
                        progress_bar.progress(25)

                        status_text.text("🔍 컬럼 분석 중...")
                        column_mappings = unifier.analyze_columns()
                        progress_bar.progress(50)

                        status_text.text("🔄 데이터 통합 중...")
                        unified_df = unifier.unify_dataframes(
                            key_columns=key_columns if key_columns else None,
                            output_format=output_format
                        )
                        progress_bar.progress(75)

                        status_text.text("✅ 완료!")
                        progress_bar.progress(100)

                        # 세션에 저장
                        st.session_state.unifier = unifier
                        st.session_state.unified_df = unified_df

                        # 성공 메시지
                        st.success("✅ 분석 및 통합이 완료되었습니다!")

                        # 결과 요약
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("처리된 파일", len(file_paths))
                        with col2:
                            original_count = sum(len(unifier.dataframes[i]['data']) for i in range(len(unifier.dataframes)))
                            st.metric("원본 행 수", original_count)
                        with col3:
                            st.metric("통합 후 행 수", len(unified_df))
                        with col4:
                            removed = original_count - len(unified_df)
                            st.metric("중복 제거", f"{removed}개", delta=f"-{removed}")

                        # 컬럼 매핑 표시
                        if column_mappings:
                            st.subheader("📌 컬럼 매핑 결과")
                            mapping_data = []
                            for unified_col, original_cols in column_mappings.items():
                                if len(original_cols) > 1:
                                    mapping_data.append({
                                        '통합 컬럼명': unified_col,
                                        '원본 컬럼명들': ', '.join(original_cols)
                                    })

                            if mapping_data:
                                st.dataframe(pd.DataFrame(mapping_data), use_container_width=True)

                        status_text.empty()
                        progress_bar.empty()

                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
                        import traceback
                        with st.expander("상세 오류 정보"):
                            st.code(traceback.format_exc())

    # Tab 3: 결과 확인
    with tab3:
        st.header("통합 결과")

        if st.session_state.unified_df is None:
            st.info("👈 먼저 데이터 분석을 실행해주세요")
        else:
            df = st.session_state.unified_df

            # 결과 통계
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 행 수", len(df))
            with col2:
                st.metric("총 컬럼 수", len(df.columns))
            with col3:
                if st.session_state.unifier:
                    original_total = sum(len(st.session_state.unifier.dataframes[i]['data']) for i in range(len(st.session_state.unifier.dataframes)))
                    duplicate_ratio = ((1 - len(df) / original_total) * 100) if original_total > 0 else 0
                    st.metric("중복 제거 비율", f"{duplicate_ratio:.1f}%")
                else:
                    st.metric("중복 제거 비율", "0.0%")

            st.divider()

            # 데이터 미리보기
            st.subheader("데이터 미리보기")

            # 필터 옵션
            col1, col2 = st.columns([3, 1])
            with col1:
                show_rows = st.slider("표시할 행 수", 5, 100, 10)
            with col2:
                if st.button("전체 데이터 보기"):
                    show_rows = len(df)

            st.dataframe(df.head(show_rows), use_container_width=True)

            # 다운로드 버튼
            st.divider()
            st.subheader("💾 결과 다운로드")

            col1, col2 = st.columns(2)

            with col1:
                # 엑셀 다운로드
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='통합결과')
                output.seek(0)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 Excel 파일 다운로드",
                    data=output,
                    file_name=f"unified_result_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            with col2:
                # CSV 다운로드
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 CSV 파일 다운로드",
                    data=csv,
                    file_name=f"unified_result_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # Tab 4: 통계
    with tab4:
        st.header("데이터 통계 및 분석")

        if st.session_state.unified_df is None:
            st.info("👈 먼저 데이터 분석을 실행해주세요")
        else:
            df = st.session_state.unified_df

            # 기본 통계
            st.subheader("📊 기본 통계")
            st.dataframe(df.describe(), use_container_width=True)

            # 컬럼별 결측치 비율
            st.subheader("📉 결측치 분석")
            missing_data = pd.DataFrame({
                '컬럼': df.columns,
                '결측치 수': df.isnull().sum().values,
                '결측치 비율 (%)': (df.isnull().sum().values / len(df) * 100).round(2)
            })

            fig = px.bar(
                missing_data,
                x='컬럼',
                y='결측치 비율 (%)',
                title='컬럼별 결측치 비율',
                color='결측치 비율 (%)',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)

            # 파일별 기여도
            if st.session_state.unifier:
                st.subheader("📈 파일별 데이터 기여도")

                file_contrib = []
                for i, file_data in enumerate(st.session_state.uploaded_files_data):
                    if i < len(st.session_state.unifier.dataframes):
                        df_info = st.session_state.unifier.dataframes[i]
                        file_contrib.append({
                            '파일명': file_data['name'],
                            '행 수': len(df_info['data']),
                            '컬럼 수': len(df_info['data'].columns)
                        })

                contrib_df = pd.DataFrame(file_contrib)

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=contrib_df['파일명'],
                    y=contrib_df['행 수'],
                    name='행 수',
                    marker_color='lightblue'
                ))
                fig.add_trace(go.Bar(
                    x=contrib_df['파일명'],
                    y=contrib_df['컬럼 수'],
                    name='컬럼 수',
                    marker_color='lightgreen'
                ))

                fig.update_layout(
                    title='파일별 데이터 현황',
                    xaxis_title='파일명',
                    yaxis_title='개수',
                    barmode='group'
                )

                st.plotly_chart(fig, use_container_width=True)

    # 푸터
    st.divider()
    footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)
    with footer_col1:
        st.caption(f"📌 버전 {__version__}")
    with footer_col2:
        st.caption(f"📅 {__release_date__}")
    with footer_col3:
        st.caption("🔗 [GitHub](https://github.com/caleblee2050/kfta_excel)")
    with footer_col4:
        st.caption("⚡ Powered by Streamlit + Gemini AI")


if __name__ == '__main__':
    main()
