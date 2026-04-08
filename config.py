# -*- coding: utf-8 -*-
"""
KB 청약요청 시스템 설정 파일
⚠️  민감 정보(API 키, 개인정보, 스프레드시트 ID)는 이 파일에 넣지 마세요.
    모든 민감 정보는 .streamlit/secrets.toml 에서 관리합니다.
"""

# ── Google Sheets 시트명 매핑 ──────────────────────────────
# SPREADSHEET_ID 는 secrets.toml 의 [spreadsheet_id] 에서 로드됩니다.
SHEET_NAMES = {
    "data": "DATA",
    "request": "청약요청",
    "log": "변경로그",
    "mailing": "메일링",
    "closure": "폐쇄관리",
    "users": "사용자",
    "prepaid_data": "선불제DATA",
    "postpaid_data": "후불제DATA",
    "prepaid_closure": "선불제해지",
    "postpaid_closure": "후불제해지",
}

# ── 분류 체계 ───────────────────────────────────────────────
SECTIONS = {
    "본지점": {
        "label": "본지점",
        "icon": "🏢",
        "color": "#3282B8",
        "data_sheet": "data",
        "closure_sheet": "closure",
        "menus": ["검색", "청약작성", "메일발송", "변경관리", "폐쇄처리", "신규등록"],
    },
    "선불제": {
        "label": "선불제",
        "icon": "📡",
        "color": "#0F9B8E",
        "data_sheet": "prepaid_data",
        "closure_sheet": "prepaid_closure",
        "menus": ["신규등록", "해지등록"],
    },
    "후불제": {
        "label": "후불제",
        "icon": "📶",
        "color": "#8B5CF6",
        "data_sheet": "postpaid_data",
        "closure_sheet": "postpaid_closure",
        "menus": ["신규등록", "해지등록"],
    },
}

# ── 본지점 옵션 ─────────────────────────────────────────────
WORK_TYPES  = ["주소지이전", "층간이전", "층내이전", "폐쇄", "신규", "감속", "증속"]
BRANCH_TYPES = ["영업점", "점", "PB센터", "지역본부", "본부부서"]
WORK_TIMES  = ["09:00~11:00", "10:00~12:00", "13:00~15:00", "14:00~16:00", "협의필요"]

# ── 선불제 옵션 ─────────────────────────────────────────────
PREPAID_USAGE_TYPES  = ["대외회선", "원격지", "DWDM", "전용회선", "본부", "클라우드", "방소용"]
PREPAID_SERVICE_NAMES = ["기업데이터", "기업인터넷"]
PREPAID_RATE_PLANS   = ["전용회선", "대외회선"]

# ── 후불제 옵션 ─────────────────────────────────────────────
POSTPAID_CATEGORIES   = ["영업점인터넷", "LTE", "인뱅/국제"]
POSTPAID_SERVICE_NAMES = ["기업데이터", "기업Managed", "광랜"]
POSTPAID_RATE_PLANS   = ["비즈광랜_스텐다드", "매니지드 M2M", "광랜", "IoT100"]

# ── 레포트 색상 팔레트 ──────────────────────────────────────
REPORT_COLORS = {
    "primary_start": "#0F4C75",
    "primary_end":   "#3282B8",
    "bar_colors": {
        "영업점":   "#3282B8",
        "점":       "#0F9B8E",
        "PB센터":   "#F28B30",
        "지역본부": "#8B5CF6",
        "본부부서": "#EC4899",
    },
    "card_total":   ("#EEF2FF", "#4F46E5"),
    "card_active":  ("#ECFDF5", "#059669"),
    "card_closed":  ("#FEF2F2", "#DC2626"),
    "card_changes": ("#FFF7ED", "#EA580C"),
    "section_colors": {
        "본지점": ("#E0F2FE", "#0369A1"),
        "선불제": ("#D1FAE5", "#047857"),
        "후불제": ("#EDE9FE", "#6D28D9"),
    },
}
