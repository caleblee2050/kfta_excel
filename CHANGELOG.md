# Changelog

All notable changes to Excel Unifier will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-11-13

### Added
- 웹 앱에 버전 정보 표시 (상단 및 푸터)
- 중복 제거 설정에 대한 상세 설명 추가 (확장 가능한 도움말)
- CHANGELOG.md 파일 생성 (버전 관리)

### Changed
- **AI 모드를 기본값으로 설정** (기존: OFF → 신규: ON)
- **KFTA 형식을 기본 출력 형식으로 설정** (기존: auto → 신규: kfta)
- 출력 형식 선택 UI 개선 (상세 설명 추가, 마크다운 형식)
- 푸터 레이아웃 개선 (버전 정보, 날짜, GitHub 링크, Powered by 정보)

### Improved
- UI 가독성 향상:
  - 중복 제거 설정에 이모지 추가
  - 키 컬럼 선택 시 실시간 피드백 표시
  - 출력 형식 설명을 더 명확하게 개선

## [1.1.0] - 2025-11-12

### Added
- 클라이언트 요구사항 반영: 중고등학교 처리 개선
- KFTA 특화 파서 (위치 기반 필드 매핑)
- 상세한 컬럼 매핑 디버깅 로그

### Fixed
- UnboundLocalError 해결: 중복 os import 제거
- 학교명 처리 로직 개선

## [1.0.0] - 2025-11-11

### Initial Release
- 자동 컬럼 매핑 (키워드 기반 + 유사도 기반)
- 스마트 값 정규화 (학교명, 이름 등)
- 지능형 중복 제거 (정규화된 값 기반)
- 통일된 양식의 엑셀 파일 출력
- CLI 인터페이스
- Streamlit 기반 웹 대시보드
- 예제 파일 생성기
- AI 모드 (Gemini API 연동)
- 3단계 하이브리드 매칭 시스템:
  1. 키워드 딕셔너리 매칭
  2. AI 의미론적 매칭
  3. Levenshtein 거리 기반 매칭

---

## Version Guidelines

### Major Version (X.0.0)
- 호환성이 깨지는 대규모 변경
- 전체 구조 재설계

### Minor Version (1.X.0)
- 새로운 기능 추가
- 기존 기능 개선
- 하위 호환성 유지

### Patch Version (1.2.X)
- 버그 수정
- 문서 업데이트
- 성능 개선
