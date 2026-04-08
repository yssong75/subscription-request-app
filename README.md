# KB 청약요청 시스템

## 개요
KB국민은행 지점 네트워크 장비 청약(이전/변경) 요청을 웹에서 작성하고 메일 발송하는 시스템입니다.

## 주요 기능
- 지점 정보 검색 (점번/지점명)
- 청약 요청서 작성
- HTML 형식 메일 자동 발송
- 청약 요청 및 변경 로그 자동 기록
- Google Sheets를 데이터베이스로 활용

## 기술 스택
- **Frontend**: Streamlit
- **Database**: Google Sheets (gspread)
- **Email**: Gmail API
- **Deployment**: Streamlit Cloud (무료)

## 파일 구조
```
subscription-request-app/
├── app.py                    # 메인 Streamlit 앱
├── config.py                 # 설정값
├── modules/
│   ├── __init__.py
│   ├── gsheet.py             # Google Sheets CRUD
│   ├── gmail.py              # Gmail 발송
│   └── utils.py              # 유틸리티
├── requirements.txt
├── .streamlit/
│   └── secrets.toml          # 로컬 테스트용 (Git에 커밋 금지)
├── atomic-vault-476812-u9-38ff07694dc6.json  # GCP 서비스 계정 키 (Git에 커밋 금지)
└── README.md
```

## 설정 정보
- **Spreadsheet ID**: `1JTjMzIU7T9oLYpu3zH3bWr-lstDzKpU7U5HoUC6rmjw`
- **Project ID**: `atomic-vault-476812-u9`
- **JSON 키 파일**: `atomic-vault-476812-u9-38ff07694dc6.json`

## Google Sheets 구조

### 1. DATA 시트 (마스터 데이터)
| 점번 | 지점명 | 전용회선 | 비즈광랜 | 속도 | AP수 | 주소1 | 상위국 | 사용여부 |

### 2. 청약요청 시트
| 요청ID | 점번 | 지점명 | 전용회선 | 비즈광랜 | 속도 | AP수 | 상위국 | 변경전주소 | 변경후주소 | 작업구분 | 요청일 | 작업시간 | 담당자 | 전화번호 | 요청사항 | 거리층 | 발송여부 | 발송시각 | 수신자 |

### 3. 변경로그 시트
| 변경시각 | 점번 | 지점명 | 이전주소 | 신규주소 | 요청일 | 작업시간 | 작업구분 |

## 로컬 개발 환경 설정

### 1. 필수 요구사항
- Python 3.8 이상
- Google Cloud Platform 서비스 계정 (JSON 키 파일)
- Google Sheets API 활성화
- Gmail API 활성화 (메일 발송 시)

### 2. 설치
```bash
# 1. 레포지토리 클론 또는 다운로드
cd subscription-request-app

# 2. 가상 환경 생성 (선택 사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt
```

### 3. GCP 서비스 계정 설정
1. Google Cloud Console에서 서비스 계정 생성
2. JSON 키 파일 다운로드
3. 파일명을 `atomic-vault-476812-u9-38ff07694dc6.json`으로 변경
4. 프로젝트 루트 디렉토리에 배치

### 4. Streamlit Secrets 설정
`.streamlit/secrets.toml` 파일을 열고 서비스 계정 JSON 내용을 복사하여 붙여넣으세요.

```toml
# Gmail 사용자 이메일
gmail_user_email = "your-email@example.com"

# GCP 서비스 계정 정보
[gcp_service_account]
type = "service_account"
project_id = "atomic-vault-476812-u9"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
# ... 나머지 필드
```

### 5. Google Sheets 권한 설정
서비스 계정 이메일 주소를 Google Sheets에 편집자로 추가하세요.
- Sheets URL: `https://docs.google.com/spreadsheets/d/1JTjMzIU7T9oLYpu3zH3bWr-lstDzKpU7U5HoUC6rmjw`

### 6. 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속합니다.

## Streamlit Cloud 배포

### 1. GitHub 레포지토리 생성
프로젝트를 GitHub에 업로드합니다.

**주의**: `.gitignore`에 다음 파일을 추가하세요:
```
.streamlit/secrets.toml
*.json
__pycache__/
*.pyc
```

### 2. Streamlit Cloud 설정
1. [Streamlit Cloud](https://streamlit.io/cloud)에 로그인
2. "New app" 클릭
3. GitHub 레포지토리 연결
4. Main file path: `app.py`
5. "Advanced settings" → "Secrets" 클릭
6. `.streamlit/secrets.toml` 내용을 복사하여 붙여넣기
7. "Deploy" 클릭

### 3. 배포 완료
몇 분 후 앱이 자동으로 배포되며, 공개 URL이 생성됩니다.

## 사용 방법

### 1단계: 지점 검색
1. "🔍 검색" 탭에서 점번 또는 지점명 입력
2. 검색 버튼 클릭
3. 결과 목록에서 원하는 지점 "선택" 버튼 클릭

### 2단계: 청약 작성
1. "✏️ 청약 작성" 탭으로 이동
2. 자동 입력된 기본 정보 확인
3. 변경 후 주소, 작업 구분, 담당자 등 수동 입력
4. "📧 발송 미리보기" 버튼 클릭

### 3단계: 메일 발송
1. "📧 발송/이력" 탭으로 이동
2. 메일 본문 미리보기 확인
3. 수신자 이메일 입력 (쉼표로 구분)
4. "✉️ 메일 발송" 버튼 클릭

## 주요 설정 변경

### 수신자 기본값 변경
`config.py` 파일에서 수정:
```python
DEFAULT_RECIPIENTS = ["receiver1@example.com", "receiver2@example.com"]
```

### 작업 구분 옵션 변경
`config.py` 파일에서 수정:
```python
WORK_TYPES = ["주소지이전", "층간이전", "층내이전", "폐쇄", "신규"]
```

### 작업 시간 옵션 변경
`config.py` 파일에서 수정:
```python
WORK_TIMES = ["09:00~11:00", "10:00~12:00", "13:00~15:00", "14:00~16:00", "협의필요"]
```

### 메일 서명 이미지 추가

메일 하단에 서명 이미지를 추가하는 방법:

#### 방법 1: 이미지 URL 사용 (권장)

1. 서명 이미지를 회사 웹 서버나 클라우드에 업로드
2. `config.py`에서 `DEFAULT_EMAIL_SIGNATURE` 수정:

```python
DEFAULT_EMAIL_SIGNATURE = """
<div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #3A7D7D;">
    <p style="margin: 5px 0;">이상입니다.</p>
    <p style="margin: 5px 0;">감사합니다.</p>
    <hr style="border: none; border-top: 1px solid #ddd; margin: 15px 0;">
    <div style="text-align: center;">
        <img src="https://your-domain.com/signature.png" width="300" alt="서명" />
    </div>
</div>
"""
```

#### 방법 2: Base64 인코딩 사용

1. 유틸리티 스크립트 실행:
```bash
python add_signature_image.py signature.png 300
```

2. 출력된 HTML 코드를 `config.py`의 `DEFAULT_EMAIL_SIGNATURE`에 복사

**참고**:
- 기본 서명("이상입니다"/"감사합니다")은 모든 메일에 자동으로 추가됩니다.
- 청약 작성 시 "추가 서명" 필드에 개인 정보를 입력하면 기본 서명 위에 추가됩니다.

## 문제 해결

### Google Sheets 인증 실패
- 서비스 계정 JSON 파일이 올바른 위치에 있는지 확인
- `.streamlit/secrets.toml` 내용이 정확한지 확인
- 서비스 계정이 Sheets에 편집자로 추가되었는지 확인

### Gmail 발송 실패
- Gmail API가 활성화되었는지 확인
- 서비스 계정이 Gmail 발송 권한을 가지고 있는지 확인
- Domain-wide delegation 설정 (G Suite 환경)

### 데이터 검색 안 됨
- Google Sheets의 "DATA" 시트 이름 확인
- 헤더 행이 첫 번째 행에 있는지 확인
- 점번, 지점명 컬럼이 존재하는지 확인

## 보안 주의사항
1. **절대 Git에 커밋하지 말 것**:
   - `.streamlit/secrets.toml`
   - `*.json` (서비스 계정 키 파일)

2. **Streamlit Cloud Secrets 사용**:
   - 배포 시 반드시 Streamlit Cloud의 Secrets 기능 사용
   - 환경 변수로 민감 정보 관리

3. **서비스 계정 권한 최소화**:
   - 필요한 Sheets/Gmail 권한만 부여
   - 정기적으로 액세스 로그 확인

## 현재 구축 현황

### 구현 완료된 기능
| 구분 | 기능 | 상태 |
|------|------|------|
| 탭 1 | 지점 검색 (점번/지점명, 부분일치) | ✅ 완료 |
| 탭 2 | 청약 작성 (자동채움 + 수동입력) | ✅ 완료 |
| 탭 2 | 이메일 미리보기 | ✅ 완료 |
| 탭 3 | HTML 이메일 발송 (TO/CC) | ✅ 완료 |
| 탭 3 | 메일링 리스트 선택 | ✅ 완료 |
| 탭 3 | 발송 이력 조회 (최근 20건) | ✅ 완료 |
| 데이터 | Google Sheets 연동 (3개 시트) | ✅ 완료 |
| 데이터 | 청약요청 자동 저장 | ✅ 완료 |
| 데이터 | 변경로그 자동 기록 | ✅ 완료 |
| 데이터 | 고유 요청ID 생성 (REQ+타임스탬프) | ✅ 완료 |
| 이메일 | HTML 서명 (연락처/회사정보) | ✅ 완료 |
| 이메일 | 이메일 주소 유효성 검증 | ✅ 완료 |
| 유틸 | 서명 이미지 Base64 변환 도구 | ✅ 완료 |
| 설정 | .gitignore 보안 설정 | ✅ 완료 |
| 문서 | README 작성 | ✅ 완료 |

### 테스트 결과
- **테스트 코드 미존재**: pytest, unittest 등 테스트 인프라가 구축되어 있지 않음
- 단위 테스트, 통합 테스트 파일 없음

### 해야 할 일 (TODO)

#### 우선순위 높음
- [ ] 테스트 코드 작성 (gsheet, gmail, utils 모듈 단위 테스트)
- [ ] 실제 수신자 이메일 설정 (`config.py`의 `DEFAULT_RECIPIENTS`가 플레이스홀더 상태)
- [ ] 메일링 리스트 실제 이메일 주소 입력 (네트워크팀/인프라팀/운영팀)
- [ ] Streamlit secrets 설정 확인 (`gmail_user_email`, `gmail_app_password`)

#### 우선순위 중간
- [ ] 에러 핸들링 강화 (Google Sheets 연결 실패, SMTP 타임아웃 등)
- [ ] 입력 폼 유효성 검증 강화 (필수 필드 누락 방지)
- [ ] 발송 실패 시 재시도 로직 추가

#### 우선순위 낮음
- [ ] Streamlit Cloud 또는 사내 서버 배포
- [ ] 사용자 인증/권한 관리 체계 도입
- [ ] UI/UX 개선 (탭 전환 시 데이터 유지, 폼 리셋 등)
- [ ] 발송 이력 필터링/검색 기능 추가

## 라이선스
내부 사용 목적으로 제작됨.

## 문의
기술 지원이 필요한 경우 시스템 관리자에게 문의하세요.
