# 🚂 Railway 배포 단계별 가이드

## 현재 상태

✅ GitHub 저장소 푸시 완료: https://github.com/caleblee2050/kfta_excel
✅ Railway 배포 설정 파일 준비 완료
✅ Railway CLI 설치 완료 (v4.11.0)

---

## 배포 방법 (2가지 옵션)

### 🌐 옵션 1: 웹 UI로 배포 (권장 - 가장 쉬움)

1. **Railway 계정 생성/로그인**
   - https://railway.app/ 접속
   - "Login with GitHub" 클릭
   - GitHub 계정으로 로그인

2. **새 프로젝트 생성**
   - 대시보드에서 "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - `caleblee2050/kfta_excel` 저장소 선택
   - Railway가 자동으로 빌드 시작

3. **환경변수 설정**
   - 프로젝트 대시보드에서 "Variables" 탭 클릭
   - "New Variable" 클릭
   - 다음 환경변수 추가:
     ```
     GEMINI_API_KEY=AIzaSyDFqJLNAJvMaE6fUtDmCGMdz7E4yYH-g9Q
     ```
   - 저장하면 자동으로 재배포

4. **배포 완료**
   - 빌드 완료 후 "Deployments" 탭에서 URL 확인
   - 예: `https://kfta-excel-production.up.railway.app`
   - 브라우저에서 접속하여 테스트

---

### 💻 옵션 2: CLI로 배포

```bash
# 1. Railway 로그인
railway login
# 브라우저가 열리면 GitHub 계정으로 로그인

# 2. 프로젝트 초기화
railway init
# 프로젝트 이름 입력: kfta-excel

# 3. 환경변수 설정
railway variables set GEMINI_API_KEY=AIzaSyDFqJLNAJvMaE6fUtDmCGMdz7E4yYH-g9Q

# 4. 배포
railway up

# 5. 배포 상태 확인
railway status

# 6. 로그 확인
railway logs

# 7. URL 열기
railway open
```

---

## 배포 후 확인 사항

### ✅ 체크리스트

1. **배포 성공 확인**
   - Railway 대시보드에서 "Deployments" 상태가 "Active" 인지 확인
   - 빌드 로그에 에러가 없는지 확인

2. **웹사이트 접속 테스트**
   - 배포된 URL 접속 (예: `https://kfta-excel-production.up.railway.app`)
   - 웹 대시보드가 정상적으로 로드되는지 확인

3. **AI 모드 테스트**
   - 사이드바에서 "🤖 AI 모드" 체크
   - "✅ API 키 확인됨" 메시지 표시되는지 확인
   - API 키가 없으면 "⚠️ .env 파일에 GEMINI_API_KEY를 설정하세요" 표시됨

4. **파일 업로드 테스트**
   - 예제 엑셀 파일 업로드
   - 분석 실행
   - 결과 다운로드

---

## 🔧 트러블슈팅

### 빌드 실패

**증상**:
```
Error: Failed to build
```

**해결**:
1. Railway 대시보드에서 "Deployments" → "View Logs" 확인
2. requirements.txt 패키지 버전 확인
3. Python 버전 확인 (runtime.txt)

### API 키 오류

**증상**:
```
⚠️ .env 파일에 GEMINI_API_KEY를 설정하세요
```

**해결**:
1. Railway 대시보드 → "Variables" 탭
2. `GEMINI_API_KEY` 환경변수 확인
3. 값이 정확한지 확인
4. "Redeploy" 클릭

### 포트 오류

**증상**:
```
Error: Port 8501 already in use
```

**해결**:
- Railway는 자동으로 `PORT` 환경변수 할당
- 우리 설정에서 `$PORT` 사용하므로 자동 해결됨
- 문제 지속 시 railway.toml 및 Procfile 확인

### 메모리 부족

**증상**:
```
Error: Out of memory
Container killed due to memory limit
```

**해결**:
1. Railway 무료 플랜: 512MB RAM 제한
2. 업그레이드 필요: Hobby Plan ($5/월, 8GB RAM)
3. 또는 코드 최적화:
   - 캐싱 활용
   - 불필요한 데이터 제거
   - 대용량 파일 처리 최적화

---

## 💰 비용 안내

### Railway 무료 플랜
- ✅ $5 무료 크레딧 (매월)
- ✅ 500시간 실행 시간
- ✅ 512MB RAM
- ✅ 1GB 디스크
- ✅ 무제한 배포

**예상 사용량**:
- 일반적인 사용: 무료 플랜으로 충분
- 24시간 운영: ~$1-2/월
- 트래픽 많은 경우: Hobby Plan 권장

### Railway Hobby Plan
- 💳 $5/월
- 🚀 8GB RAM
- 💾 무제한 디스크
- 🔄 우선 지원

---

## 🌐 커스텀 도메인 (옵션)

### 도메인 연결 방법

1. **Railway 대시보드**
   - "Settings" 탭 → "Domains" 섹션
   - "Add Domain" 클릭
   - 도메인 입력 (예: `excel.yourdomain.com`)

2. **DNS 설정**
   - 도메인 제공업체 (가비아, 카페24 등)에서:
   ```
   Type: CNAME
   Name: excel
   Value: kfta-excel-production.up.railway.app
   ```

3. **SSL 인증서**
   - Railway가 자동으로 Let's Encrypt SSL 발급
   - 몇 분 후 HTTPS 자동 활성화

---

## 📊 모니터링

### Railway 대시보드에서 확인 가능

1. **Metrics (메트릭)**
   - CPU 사용량
   - 메모리 사용량
   - 네트워크 트래픽

2. **Deployments (배포)**
   - 배포 이력
   - 빌드 로그
   - 배포 시간

3. **Logs (로그)**
   - 실시간 애플리케이션 로그
   - 에러 추적
   - 디버깅 정보

4. **Usage (사용량)**
   - 실행 시간
   - 크레딧 소비
   - 비용 추정

---

## 🔄 자동 배포 (CI/CD)

GitHub 저장소에 푸시하면 Railway가 자동으로:

1. ✅ 변경 감지
2. ✅ 빌드 시작
3. ✅ 테스트 실행 (있을 경우)
4. ✅ 배포 완료
5. ✅ 이전 버전 롤백 가능

```bash
# 로컬에서 수정 후
git add .
git commit -m "Update feature"
git push origin main

# Railway가 자동으로 감지하고 배포 시작
# 대시보드에서 실시간 진행 상황 확인 가능
```

---

## 📱 배포 후 공유

배포 완료 후 URL을 팀원들과 공유:

```
🎉 Excel Unifier 배포 완료!

웹사이트: https://kfta-excel-production.up.railway.app

사용 방법:
1. 위 URL 접속
2. 사이드바에서 "🤖 AI 모드" 활성화
3. 엑셀 파일 업로드
4. 키 컬럼 선택 후 "🚀 분석 및 통합 실행"
5. 결과 다운로드

기능:
✅ 자동 컬럼 매핑
✅ AI 기반 유사도 분석
✅ 스마트 중복 제거
✅ Excel/CSV 다운로드
```

---

## 🆘 도움말

### Railway 지원
- 📚 공식 문서: https://docs.railway.app/
- 💬 Discord: https://discord.gg/railway
- 📧 이메일: team@railway.app

### 프로젝트 이슈
- 🐛 GitHub Issues: https://github.com/caleblee2050/kfta_excel/issues
- 📖 프로젝트 문서: README.md, AI_SETUP.md

---

## ✅ 다음 단계

배포 후 할 수 있는 것들:

1. **실제 데이터 테스트**
   - 실제 엑셀 파일 업로드
   - AI 모드와 기본 모드 비교
   - 결과 검증

2. **성능 모니터링**
   - Railway 대시보드에서 메트릭 확인
   - 응답 시간 측정
   - 에러율 추적

3. **피드백 수집**
   - 사용자 의견 수집
   - 개선 사항 파악
   - 버그 리포트

4. **기능 개선**
   - 추가 기능 개발
   - UI/UX 개선
   - 성능 최적화

---

**배포 준비 완료!** 🚀

위 두 가지 방법 중 선택하여 Railway에 배포하세요.
웹 UI 방법(옵션 1)이 더 간단하고 직관적입니다.
