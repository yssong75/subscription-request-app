-- ============================================================
-- KB 청약요청 시스템 - Supabase PostgreSQL 스키마
-- Google Sheets 10개 시트 → 정규화된 8개 테이블
-- ============================================================

-- ── 확장 기능 ────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- 한글 검색 성능 향상


-- ============================================================
-- 1. 사용자 (users) - 구 "사용자" 시트
-- ============================================================
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    아이디      TEXT NOT NULL UNIQUE,
    비밀번호    TEXT NOT NULL,          -- bcrypt 해시
    이름        TEXT NOT NULL,
    이메일      TEXT,
    권한        TEXT NOT NULL DEFAULT '일반' CHECK (권한 IN ('관리자', '일반')),
    상태        TEXT NOT NULL DEFAULT '활성' CHECK (상태 IN ('활성', '비활성')),
    등록일      TIMESTAMPTZ DEFAULT NOW(),
    최근로그인  TIMESTAMPTZ
);

-- ============================================================
-- 2. 메일링 리스트 (mailing_list) - 구 "메일링" 시트
-- ============================================================
CREATE TABLE mailing_list (
    id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    이름    TEXT NOT NULL,
    이메일  TEXT NOT NULL UNIQUE
);

-- ============================================================
-- 3. 본지점 회선 (branch_lines) - 구 "DATA" 시트
-- ============================================================
CREATE TABLE branch_lines (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    점번        TEXT NOT NULL,
    지점명      TEXT NOT NULL,
    점포구분    TEXT CHECK (점포구분 IN ('영업점', '점', 'PB센터', '지역본부', '본부부서')),
    전용회선    TEXT,
    vlan_id     TEXT,
    비즈광랜    TEXT,
    속도        TEXT,
    ap수        TEXT,
    주소        TEXT,
    상위국      TEXT,
    사용여부    TEXT NOT NULL DEFAULT 'Y' CHECK (사용여부 IN ('Y', 'N')),
    등록일      TIMESTAMPTZ DEFAULT NOW(),
    수정일      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_branch_lines_점번    ON branch_lines(점번);
CREATE INDEX idx_branch_lines_지점명  ON branch_lines USING gin(지점명 gin_trgm_ops);
CREATE INDEX idx_branch_lines_사용여부 ON branch_lines(사용여부);

-- ============================================================
-- 4. 본지점 폐쇄 (branch_closures) - 구 "폐쇄관리" 시트
-- ============================================================
CREATE TABLE branch_closures (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    점번        TEXT NOT NULL,
    지점명      TEXT NOT NULL,
    점포구분    TEXT,
    전용회선    TEXT,
    vlan_id     TEXT,
    비즈광랜    TEXT,
    속도        TEXT,
    ap수        TEXT,
    주소        TEXT,
    상위국      TEXT,
    폐쇄일      DATE DEFAULT CURRENT_DATE,
    등록일      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 5. 청약 요청 (requests) - 구 "청약요청" 시트
-- ============================================================
CREATE TABLE requests (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    요청id          TEXT UNIQUE,                    -- 기존 요청ID 형식 유지
    점번            TEXT NOT NULL,
    지점명          TEXT NOT NULL,
    전용회선        TEXT,
    vlan_id         TEXT,
    비즈광랜        TEXT,
    속도            TEXT,
    ap수            TEXT,
    상위국          TEXT,
    변경전주소      TEXT,
    변경후주소      TEXT,
    작업구분        TEXT,
    요청일          DATE,
    작업시간        TEXT,
    담당자          TEXT,
    전화번호        TEXT,
    요청사항        TEXT,
    거리층          TEXT,
    발송여부        TEXT DEFAULT 'N',
    발송시각        TIMESTAMPTZ,
    등록일          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_requests_점번   ON requests(점번);
CREATE INDEX idx_requests_등록일 ON requests(등록일 DESC);

-- ============================================================
-- 6. 변경 로그 (change_logs) - 구 "변경로그" 시트 (통합)
-- ============================================================
CREATE TABLE change_logs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    분류        TEXT NOT NULL CHECK (분류 IN ('본지점', '선불제', '후불제')),
    점번        TEXT,
    지점명      TEXT,
    이전주소    TEXT,
    신규주소    TEXT,
    요청일      TEXT,
    작업시간    TEXT,
    작업구분    TEXT,
    변경요약    TEXT,
    전용회선    TEXT,
    비즈광랜    TEXT,
    등록일      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_change_logs_분류   ON change_logs(분류);
CREATE INDEX idx_change_logs_점번   ON change_logs(점번);
CREATE INDEX idx_change_logs_등록일 ON change_logs(등록일 DESC);

-- ============================================================
-- 7. 선불제 회선 (prepaid_lines) - 구 "선불제DATA" 시트
-- ============================================================
CREATE TABLE prepaid_lines (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    점번            TEXT,
    지점명          TEXT NOT NULL,
    서비스번호      TEXT,
    서비스명        TEXT,
    요금제          TEXT,
    용도            TEXT,
    다운속도        TEXT,
    업속도          TEXT,
    비용            TEXT,
    계약일          DATE,
    계약기간        TEXT,
    상태            TEXT DEFAULT '활성' CHECK (상태 IN ('활성', '해지')),
    등록일          TIMESTAMPTZ DEFAULT NOW(),
    수정일          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prepaid_lines_서비스번호 ON prepaid_lines(서비스번호);
CREATE INDEX idx_prepaid_lines_지점명    ON prepaid_lines USING gin(지점명 gin_trgm_ops);
CREATE INDEX idx_prepaid_lines_상태      ON prepaid_lines(상태);

-- ============================================================
-- 8. 선불제 해지 (prepaid_closures) - 구 "선불제해지" 시트
-- ============================================================
CREATE TABLE prepaid_closures (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    점번            TEXT,
    지점명          TEXT,
    서비스번호      TEXT,
    서비스명        TEXT,
    요금제          TEXT,
    용도            TEXT,
    해지일          DATE DEFAULT CURRENT_DATE,
    해지사유        TEXT,
    등록일          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 9. 후불제 회선 (postpaid_lines) - 구 "후불제DATA" 시트
-- ============================================================
CREATE TABLE postpaid_lines (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    구분            TEXT CHECK (구분 IN ('영업점인터넷', 'LTE', '인뱅/국제')),
    점번            TEXT,
    지점명          TEXT NOT NULL,
    서비스번호      TEXT,
    서비스명        TEXT,
    요금제          TEXT,
    lte번호         TEXT,           -- LTE 전용
    코너명          TEXT,           -- LTE 전용
    wifi수량        TEXT,           -- LTE 전용
    비용            TEXT,
    계약일          DATE,
    상태            TEXT DEFAULT '활성' CHECK (상태 IN ('활성', '해지')),
    등록일          TIMESTAMPTZ DEFAULT NOW(),
    수정일          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_postpaid_lines_서비스번호 ON postpaid_lines(서비스번호);
CREATE INDEX idx_postpaid_lines_지점명    ON postpaid_lines USING gin(지점명 gin_trgm_ops);
CREATE INDEX idx_postpaid_lines_구분      ON postpaid_lines(구분);
CREATE INDEX idx_postpaid_lines_상태      ON postpaid_lines(상태);

-- ============================================================
-- 10. 후불제 해지 (postpaid_closures) - 구 "후불제해지" 시트
-- ============================================================
CREATE TABLE postpaid_closures (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    구분            TEXT,
    점번            TEXT,
    지점명          TEXT,
    서비스번호      TEXT,
    서비스명        TEXT,
    요금제          TEXT,
    해지일          DATE DEFAULT CURRENT_DATE,
    해지사유        TEXT,
    등록일          TIMESTAMPTZ DEFAULT NOW()
);


-- ============================================================
-- 자동 수정일 갱신 트리거
-- ============================================================
CREATE OR REPLACE FUNCTION update_수정일()
RETURNS TRIGGER AS $$
BEGIN
    NEW.수정일 = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_branch_lines_수정일
    BEFORE UPDATE ON branch_lines
    FOR EACH ROW EXECUTE FUNCTION update_수정일();

CREATE TRIGGER trg_prepaid_lines_수정일
    BEFORE UPDATE ON prepaid_lines
    FOR EACH ROW EXECUTE FUNCTION update_수정일();

CREATE TRIGGER trg_postpaid_lines_수정일
    BEFORE UPDATE ON postpaid_lines
    FOR EACH ROW EXECUTE FUNCTION update_수정일();


-- ============================================================
-- Row Level Security (RLS) - 인증된 사용자만 접근
-- ============================================================
ALTER TABLE users           ENABLE ROW LEVEL SECURITY;
ALTER TABLE mailing_list    ENABLE ROW LEVEL SECURITY;
ALTER TABLE branch_lines    ENABLE ROW LEVEL SECURITY;
ALTER TABLE branch_closures ENABLE ROW LEVEL SECURITY;
ALTER TABLE requests        ENABLE ROW LEVEL SECURITY;
ALTER TABLE change_logs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE prepaid_lines   ENABLE ROW LEVEL SECURITY;
ALTER TABLE prepaid_closures ENABLE ROW LEVEL SECURITY;
ALTER TABLE postpaid_lines  ENABLE ROW LEVEL SECURITY;
ALTER TABLE postpaid_closures ENABLE ROW LEVEL SECURITY;

-- Streamlit 서버(service_role)는 RLS 우회 → 앱에서 anon key 대신 service_role key 사용
