#!/bin/bash

# Excel Unifier 웹 대시보드 실행 스크립트

echo "======================================"
echo "📊 Excel Unifier 웹 대시보드"
echo "======================================"
echo ""

# 가상환경이 없으면 생성
if [ ! -d "venv" ]; then
    echo "🔧 가상환경 생성 중..."
    python3 -m venv venv
    echo "📦 패키지 설치 중..."
    venv/bin/pip install -r requirements.txt
fi

echo "🚀 웹 애플리케이션 시작 중..."
echo ""
echo "브라우저에서 자동으로 열립니다."
echo "수동으로 열려면: http://localhost:8501"
echo ""
echo "종료하려면: Ctrl+C"
echo ""

# Streamlit 앱 실행
venv/bin/streamlit run app.py
