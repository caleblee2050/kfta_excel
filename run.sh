#!/bin/bash

# Excel Unifier 실행 스크립트

# 가상환경이 없으면 생성
if [ ! -d "venv" ]; then
    echo "🔧 가상환경 생성 중..."
    python3 -m venv venv
    echo "📦 패키지 설치 중..."
    venv/bin/pip install -r requirements.txt
fi

# Python 스크립트 실행
venv/bin/python excel_unifier.py "$@"
