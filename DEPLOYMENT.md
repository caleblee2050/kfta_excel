# 🚀 Railway 배포 가이드

## Railway.app에 배포하기

### 1️⃣ Railway 계정 준비

1. [Railway.app](https://railway.app/) 접속
2. GitHub 계정으로 로그인

### 2️⃣ 프로젝트 배포

#### 방법 A: GitHub 연동 (권장)

1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. `caleblee2050/kfta_excel` 저장소 선택
4. Railway가 자동으로 빌드 시작

#### 방법 B: Railway CLI 사용

```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 배포
railway up
```

### 3️⃣ 환경변수 설정

Railway 대시보드에서:

1. 프로젝트 선택
2. "Variables" 탭 클릭
3. 환경변수 추가:
   ```
   GEMINI_API_KEY=AIzaSyDFqJLNAJvMaE6fUtDmCGMdz7E4yYH-g9Q
   ```
4. "Deploy" 클릭하여 재배포

### 4️⃣ 배포 확인

1. 배포 완료 후 자동으로 URL 생성 (예: `https://kfta-excel-production.up.railway.app`)
2. 브라우저에서 접속하여 테스트
3. AI 모드 토글 시 "✅ API 키 확인됨" 표시 확인

---

## 배포 파일 설명

### [railway.toml](railway.toml)
Railway 배포 설정 파일
- Nixpacks 빌더 사용
- Streamlit 시작 명령어
- 헬스체크 설정

### [Procfile](Procfile)
프로세스 시작 명령어
- Railway에서 자동 인식
- PORT 환경변수 사용

### [runtime.txt](runtime.txt)
Python 버전 지정
- Python 3.11.0

### [.streamlit/config.toml](.streamlit/config.toml)
Streamlit 서버 설정
- 헤드리스 모드
- CORS 비활성화
- 프로덕션 최적화

### [requirements.txt](requirements.txt)
Python 패키지 의존성
- Railway가 자동으로 설치

---

## 🔧 트러블슈팅

### 빌드 실패
```
Error: Failed to install packages
```
**해결**: requirements.txt 확인 및 패키지 버전 조정

### 포트 오류
```
Error: Port already in use
```
**해결**: Railway는 자동으로 PORT 환경변수 할당 (코드에서 $PORT 사용)

### API 키 오류
```
⚠️ .env 파일에 GEMINI_API_KEY를 설정하세요
```
**해결**: Railway 대시보드에서 환경변수 설정

### 메모리 부족
```
Error: Out of memory
```
**해결**: Railway 플랜 업그레이드 또는 코드 최적화

---

## 💰 비용

Railway 무료 플랜:
- $5 무료 크레딧 (매월)
- 500시간 실행 시간
- 512MB RAM
- 1GB 디스크

**예상 비용**: 개인 프로젝트는 무료 플랜으로 충분

---

## 🌐 커스텀 도메인

1. Railway 대시보드에서 "Settings" 탭
2. "Custom Domain" 섹션
3. 도메인 입력 (예: `excel.yourdomain.com`)
4. DNS 레코드 설정:
   ```
   CNAME excel yourdomain.up.railway.app
   ```

---

## 📊 모니터링

Railway 대시보드에서 확인 가능:
- 📈 CPU/메모리 사용량
- 📝 배포 로그
- 🔄 재시작 횟수
- 🌐 트래픽 통계

---

## 🔄 자동 배포

GitHub 저장소에 푸시하면 Railway가 자동으로:
1. 변경 감지
2. 빌드 시작
3. 테스트 실행
4. 배포 완료

```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway가 자동으로 배포 시작
```

---

## 📞 지원

- Railway 문서: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/caleblee2050/kfta_excel/issues

---

*배포 준비 완료! Railway에서 즉시 배포 가능합니다.* 🚀
