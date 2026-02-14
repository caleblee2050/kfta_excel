#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Unifier - 웹 대시보드
KFTA 표준 형식 전용 UI
"""

import io
import os
import tempfile
from datetime import datetime
from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st

try:
    from .excel_unifier import ExcelUnifier
except ImportError:
    from excel_unifier import ExcelUnifier

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False


__version__ = "1.5.0"
__release_date__ = "2026-02-14"

st.set_page_config(
    page_title="KFTA Excel Unifier",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

:root {
  --bg: #f4f6f8;
  --panel: #ffffff;
  --ink: #111827;
  --muted: #4b5563;
  --line: #d6dde4;
  --brand: #0f4c81;
  --brand-dark: #0b3a62;
}

html, body, [class*="css"]  {
  font-family: "Pretendard", "Noto Sans KR", "Segoe UI", sans-serif;
}

.stApp {
  background:
    radial-gradient(1000px 280px at 10% -10%, #e5edf7 0%, transparent 60%),
    radial-gradient(800px 240px at 90% -20%, #e9eef4 0%, transparent 62%),
    var(--bg);
}

.shell-title {
  font-size: 2rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  color: var(--ink);
  margin-bottom: 0.25rem;
}

.shell-sub {
  font-size: 0.98rem;
  color: var(--muted);
  margin-bottom: 0.75rem;
}

.notice {
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
  color: var(--muted);
  margin-bottom: 1rem;
}

.stButton button[kind="primary"] {
  background: linear-gradient(90deg, var(--brand), var(--brand-dark));
  border: 0;
  border-radius: 10px;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.4rem;
}

.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)


def _normalize_missing(value) -> bool:
    if pd.isna(value):
        return True
    text = str(value).strip().lower()
    return text in {"", "nan", "none", "null"}


def _quality_summary(df: pd.DataFrame) -> Dict[str, float]:
    if df is None or df.empty:
        return {"quality_score": 0.0, "missing_ratio": 100.0, "issue_rows": 0}

    key_candidates = ["이름", "현재교육청", "현재분회", "발령교육청", "발령분회", "과목", "직위"]
    key_columns = [c for c in key_candidates if c in df.columns and (~df[c].map(_normalize_missing)).any()]
    if not key_columns:
        key_columns = list(df.columns[: min(len(df.columns), 5)])

    checks = df[key_columns].apply(lambda col: col.map(_normalize_missing))
    missing_ratio = float(checks.mean().mean() * 100)
    issue_threshold = max(2, (len(key_columns) + 1) // 2)
    issue_rows = int((checks.sum(axis=1) >= issue_threshold).sum())
    quality_score = max(0.0, min(100.0, 100.0 - missing_ratio))
    return {
        "quality_score": round(quality_score, 1),
        "missing_ratio": round(missing_ratio, 1),
        "issue_rows": issue_rows,
    }


def _issue_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    key_columns = [
        c for c in ["이름", "현재교육청", "현재분회", "발령교육청", "발령분회", "과목", "직위"]
        if c in df.columns and (~df[c].map(_normalize_missing)).any()
    ]
    if not key_columns:
        return pd.DataFrame()

    checks = df[key_columns].apply(lambda col: col.map(_normalize_missing))
    issue_threshold = max(2, (len(key_columns) + 1) // 2)
    issue_mask = checks.sum(axis=1) >= issue_threshold
    issues = df.loc[issue_mask, key_columns].copy()
    issues.insert(0, "빈핵심필드수", checks.loc[issue_mask].sum(axis=1))
    return issues.sort_values("빈핵심필드수", ascending=False)


def _init_state() -> None:
    if "unifier" not in st.session_state:
        st.session_state.unifier = None
    if "unified_df" not in st.session_state:
        st.session_state.unified_df = None
    if "uploaded_files_data" not in st.session_state:
        st.session_state.uploaded_files_data = []
    if "quality" not in st.session_state:
        st.session_state.quality = None


def _sidebar_controls():
    with st.sidebar:
        st.header("처리 설정")

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        gemini_model_default = os.getenv("GEMINI_MODEL", "gemini-3-flash")

        st.caption("출력 형식: KFTA 표준으로 고정")

        use_ai = st.checkbox(
            "AI 매칭 사용",
            value=bool(api_key),
            help="의미 기반 매칭(동의어/약어/영문)을 활성화합니다.",
        )
        gemini_model = gemini_model_default

        if use_ai:
            if api_key:
                st.success("GEMINI_API_KEY 확인됨")
            else:
                st.warning("GEMINI_API_KEY 미설정 상태입니다. AI 요청이 실패하면 기본 매칭으로 동작합니다.")
            gemini_model = st.text_input("Gemini 모델", value=gemini_model_default)

        threshold = st.slider("유사도 임계값", min_value=0, max_value=100, value=85)

        dedup_keys_raw = st.text_input(
            "중복 제거 키 컬럼",
            value="이름 현재분회",
            help="공백으로 구분하세요. 예) 이름 현재분회",
        )
        dedup_keys = [key.strip() for key in dedup_keys_raw.split() if key.strip()]

        drop_issue_rows = st.checkbox(
            "핵심 필드 공란 행 제거",
            value=True,
            help="핵심 필드가 대부분 비어 있는 행을 결과에서 제외합니다.",
        )

        st.divider()
        st.caption(f"Version {__version__} ({__release_date__})")
        st.caption("KFTA 전용 통합 워크플로우")

        return use_ai, gemini_model, threshold, dedup_keys, drop_issue_rows


def _render_header() -> None:
    st.markdown('<div class="shell-title">강원교총 엑셀 통합</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="shell-sub">복수 파일을 KFTA 표준으로 통합하고 품질을 바로 확인합니다.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="notice">1) 파일 업로드 → 2) 통합 실행 → 3) 품질 검토 → 4) 엑셀 다운로드</div>',
        unsafe_allow_html=True,
    )


def _save_uploaded_files(uploaded_files):
    file_info = []
    st.session_state.uploaded_files_data = []

    for file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
            tmp.write(file.getvalue())
            tmp_path = tmp.name

        st.session_state.uploaded_files_data.append(
            {"name": file.name, "path": tmp_path, "size": file.size}
        )

        try:
            if file.name.endswith(".csv"):
                df = pd.read_csv(tmp_path)
                file_info.append(
                    {
                        "파일명": file.name,
                        "시트": "-",
                        "행 수": len(df),
                        "컬럼 수": len(df.columns),
                        "크기": f"{file.size / 1024:.1f} KB",
                    }
                )
            else:
                excel_file = pd.ExcelFile(tmp_path)
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(tmp_path, sheet_name=sheet_name)
                    if df.empty or len(df.columns) == 0:
                        continue
                    file_info.append(
                        {
                            "파일명": file.name,
                            "시트": sheet_name,
                            "행 수": len(df),
                            "컬럼 수": len(df.columns),
                            "크기": f"{file.size / 1024:.1f} KB",
                        }
                    )
        except Exception as error:
            st.error(f"{file.name} 읽기 실패: {error}")

    if file_info:
        st.dataframe(pd.DataFrame(file_info), use_container_width=True)


def main():
    _init_state()
    _render_header()
    use_ai, gemini_model, threshold, dedup_keys, drop_issue_rows = _sidebar_controls()

    tab1, tab2, tab3 = st.tabs(["파일 업로드", "통합 실행", "결과/품질"])

    with tab1:
        uploaded_files = st.file_uploader(
            "엑셀 파일 업로드 (.xlsx, .xls, .csv)",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
        )
        if uploaded_files:
            st.success(f"{len(uploaded_files)}개 파일 업로드 완료")
            _save_uploaded_files(uploaded_files)

    with tab2:
        if not st.session_state.uploaded_files_data:
            st.info("먼저 파일을 업로드하세요.")
        else:
            st.write(f"{len(st.session_state.uploaded_files_data)}개 파일 준비됨")
            if st.button("통합 실행", type="primary", use_container_width=True):
                with st.spinner("통합 처리 중..."):
                    try:
                        unifier = ExcelUnifier(
                            similarity_threshold=threshold,
                            use_ai=use_ai,
                            gemini_model=gemini_model,
                        )
                        file_paths = [f["path"] for f in st.session_state.uploaded_files_data]

                        progress = st.progress(0)
                        progress.progress(20)
                        unifier.load_excel_files(file_paths)

                        progress.progress(45)
                        column_mappings = unifier.analyze_columns()

                        progress.progress(75)
                        unified_df = unifier.unify_dataframes(
                            key_columns=dedup_keys or None,
                            output_format="kfta",
                        )

                        if drop_issue_rows and not unified_df.empty:
                            core_cols = [c for c in ["이름", "현재분회", "발령분회", "과목", "직위"] if c in unified_df.columns]
                            if core_cols:
                                mask_has_value = unified_df[core_cols].apply(
                                    lambda row: any(not _normalize_missing(v) for v in row),
                                    axis=1,
                                )
                                unified_df = unified_df[mask_has_value].reset_index(drop=True)

                        progress.progress(100)

                        st.session_state.unifier = unifier
                        st.session_state.unified_df = unified_df
                        st.session_state.quality = _quality_summary(unified_df)

                        st.success("KFTA 통합이 완료되었습니다.")

                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("처리된 파일", len(file_paths))
                        with m2:
                            original_count = sum(len(info["data"]) for info in unifier.dataframes)
                            st.metric("원본 행 수", original_count)
                        with m3:
                            st.metric("통합 후 행 수", len(unified_df))

                        with st.expander("컬럼 매핑 보기"):
                            mapping_data = []
                            for unified_col, original_cols in column_mappings.items():
                                if len(original_cols) > 1:
                                    mapping_data.append(
                                        {"통합 컬럼": unified_col, "원본 컬럼들": ", ".join(original_cols)}
                                    )
                            if mapping_data:
                                st.dataframe(pd.DataFrame(mapping_data), use_container_width=True)

                    except Exception as error:
                        st.error(f"통합 실패: {error}")

    with tab3:
        df = st.session_state.unified_df
        if df is None:
            st.info("통합 실행 후 결과가 표시됩니다.")
            return

        quality = st.session_state.quality or _quality_summary(df)
        q1, q2, q3 = st.columns(3)
        with q1:
            st.metric("품질 점수", f"{quality['quality_score']} / 100")
        with q2:
            st.metric("핵심 필드 결측률", f"{quality['missing_ratio']}%")
        with q3:
            st.metric("문제 가능 행", quality["issue_rows"])

        st.divider()
        show_rows = st.slider("미리보기 행 수", 5, 200, 20)
        st.dataframe(df.head(show_rows), use_container_width=True)

        issues = _issue_rows(df)
        with st.expander("품질 이슈 상세", expanded=False):
            if issues.empty:
                st.success("핵심 필드 공란이 많은 행이 없습니다.")
            else:
                st.warning(f"핵심 필드 결측이 많은 행 {len(issues)}건")
                st.dataframe(issues.head(200), use_container_width=True)

        st.divider()
        missing_data = pd.DataFrame(
            {
                "컬럼": df.columns,
                "결측치 비율(%)": (df.isnull().sum().values / max(1, len(df)) * 100).round(2),
            }
        ).sort_values("결측치 비율(%)", ascending=False)
        fig = px.bar(
            missing_data,
            x="컬럼",
            y="결측치 비율(%)",
            color="결측치 비율(%)",
            color_continuous_scale="Blues",
            title="컬럼별 결측치 비율",
        )
        st.plotly_chart(fig, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="KFTA_통합결과")
        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="KFTA Excel 다운로드",
            data=output,
            file_name=f"kfta_unified_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
