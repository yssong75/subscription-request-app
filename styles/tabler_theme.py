# -*- coding: utf-8 -*-
"""
Tabler 스타일 테마 - Streamlit 커스텀 CSS
"""

# Tabler 컬러 팔레트
COLORS = {
    "primary": "#066fd1",
    "primary_light": "#4299e1",
    "primary_dark": "#4263eb",
    "secondary": "#ae3ec9",
    "success": "#2fb344",
    "success_light": "#74b816",
    "success_dark": "#0ca678",
    "info": "#17a2b8",
    "warning": "#f59f00",
    "danger": "#d63939",
    "danger_light": "#d6336c",
    "orange": "#f76707",
    "cyan": "#17a2b8",
    "white": "#ffffff",
    "light": "#f8f9fa",
    "gray_100": "#f1f5f9",
    "gray_200": "#e2e8f0",
    "gray_300": "#cbd5e1",
    "gray_400": "#94a3b8",
    "gray_500": "#64748b",
    "gray_600": "#475569",
    "gray_700": "#334155",
    "gray_800": "#1e293b",
    "dark": "#1e293b",
    "body_bg": "#f1f5f9",
    "card_bg": "#ffffff",
    "border": "#e2e8f0",
}

def get_tabler_css():
    """Tabler 스타일 CSS 반환"""
    return f"""
    <style>
    /* ===== 전체 배경 및 기본 스타일 ===== */
    .stApp {{
        background-color: {COLORS['body_bg']};
    }}

    /* ===== 사이드바 스타일 ===== */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['dark']};
        padding-top: 1rem;
    }}

    [data-testid="stSidebar"] .stMarkdown {{
        color: {COLORS['white']};
    }}

    /* ===== 헤더 스타일 ===== */
    .main-header {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
        padding: 1.5rem 2rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 1.5rem;
    }}

    .main-header h1 {{
        color: white !important;
        font-weight: 600;
        margin: 0;
    }}

    /* ===== 카드 스타일 ===== */
    .tabler-card {{
        background: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .tabler-card-header {{
        font-size: 0.875rem;
        font-weight: 600;
        color: {COLORS['gray_600']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }}

    .tabler-card-value {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLORS['gray_800']};
    }}

    .tabler-card-trend {{
        font-size: 0.875rem;
        margin-left: 0.5rem;
    }}

    .trend-up {{
        color: {COLORS['success']};
    }}

    .trend-down {{
        color: {COLORS['danger']};
    }}

    /* ===== 탭 스타일 ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: {COLORS['card_bg']};
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem 0 1rem;
        gap: 0;
        border-bottom: 1px solid {COLORS['border']};
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border: none;
        color: {COLORS['gray_500']};
        font-weight: 500;
        padding: 0.75rem 1.25rem;
        border-radius: 6px 6px 0 0;
        margin-right: 0.25rem;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: {COLORS['primary']};
        background-color: {COLORS['gray_100']};
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['card_bg']} !important;
        color: {COLORS['primary']} !important;
        border: 1px solid {COLORS['border']} !important;
        border-bottom: 2px solid {COLORS['card_bg']} !important;
        margin-bottom: -1px;
    }}

    .stTabs [data-baseweb="tab-panel"] {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1.5rem;
    }}

    /* ===== 버튼 스타일 ===== */
    .stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.15s ease;
    }}

    .stButton > button:hover {{
        background-color: {COLORS['primary_dark']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    .stButton > button[kind="secondary"] {{
        background-color: {COLORS['gray_100']};
        color: {COLORS['gray_700']};
        border: 1px solid {COLORS['border']};
    }}

    .stButton > button[kind="secondary"]:hover {{
        background-color: {COLORS['gray_200']};
    }}

    /* Primary 버튼 (폼 제출 등) */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1.25rem;
        font-weight: 500;
    }}

    .stFormSubmitButton > button:hover {{
        opacity: 0.9;
        box-shadow: 0 4px 12px rgba(6,111,209,0.3);
    }}

    /* ===== 입력 필드 스타일 ===== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {{
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        background-color: {COLORS['white']};
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 0 3px rgba(6,111,209,0.15);
        outline: none;
    }}

    /* 비활성화된 입력 필드 */
    .stTextInput > div > div > input:disabled {{
        background-color: {COLORS['gray_100']};
        color: {COLORS['gray_500']};
    }}

    /* ===== 라벨 스타일 ===== */
    .stTextInput > label,
    .stSelectbox > label,
    .stTextArea > label {{
        color: {COLORS['gray_700']};
        font-weight: 500;
        font-size: 0.875rem;
        margin-bottom: 0.375rem;
    }}

    /* ===== 알림 메시지 스타일 ===== */
    .stSuccess {{
        background-color: #d1fae5;
        border: 1px solid {COLORS['success']};
        color: #065f46;
        border-radius: 6px;
        padding: 0.75rem 1rem;
    }}

    .stError {{
        background-color: #fee2e2;
        border: 1px solid {COLORS['danger']};
        color: #991b1b;
        border-radius: 6px;
    }}

    .stWarning {{
        background-color: #fef3c7;
        border: 1px solid {COLORS['warning']};
        color: #92400e;
        border-radius: 6px;
    }}

    .stInfo {{
        background-color: #dbeafe;
        border: 1px solid {COLORS['primary']};
        color: #1e40af;
        border-radius: 6px;
    }}

    /* ===== 데이터프레임 스타일 ===== */
    .stDataFrame {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        overflow: hidden;
    }}

    .stDataFrame thead th {{
        background-color: {COLORS['gray_100']};
        color: {COLORS['gray_700']};
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }}

    /* ===== 구분선 스타일 ===== */
    hr {{
        border: none;
        border-top: 1px solid {COLORS['border']};
        margin: 1.5rem 0;
    }}

    /* ===== 메트릭 카드 스타일 ===== */
    [data-testid="stMetricValue"] {{
        font-size: 1.75rem;
        font-weight: 700;
        color: {COLORS['gray_800']};
    }}

    [data-testid="stMetricLabel"] {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {COLORS['gray_500']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    [data-testid="stMetricDelta"] svg {{
        display: none;
    }}

    /* ===== 폼 컨테이너 ===== */
    [data-testid="stForm"] {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 1.5rem;
    }}

    /* ===== 스피너 ===== */
    .stSpinner > div {{
        border-color: {COLORS['primary']} transparent transparent transparent;
    }}

    /* ===== 로그인 페이지 전용 스타일 ===== */
    .login-container {{
        max-width: 400px;
        margin: 2rem auto;
        background: {COLORS['card_bg']};
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 10px 20px rgba(0,0,0,0.05);
        padding: 2rem;
    }}

    .login-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}

    .login-header h1 {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {COLORS['gray_800']};
        margin-bottom: 0.5rem;
    }}

    .login-header p {{
        color: {COLORS['gray_500']};
        font-size: 0.875rem;
    }}

    .login-logo {{
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
        border-radius: 8px;
        margin: 0 auto 1rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
    }}

    /* ===== 유저 드롭다운 ===== */
    .user-dropdown {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        border-radius: 6px;
        cursor: pointer;
    }}

    .user-dropdown:hover {{
        background-color: {COLORS['gray_100']};
    }}

    .user-avatar {{
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_dark']} 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.875rem;
    }}

    /* ===== 반응형 ===== */
    @media (max-width: 768px) {{
        .stTabs [data-baseweb="tab"] {{
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
        }}
    }}
    </style>
    """


def get_login_page_css():
    """로그인 페이지 전용 CSS"""
    return f"""
    <style>
    /* 로그인 페이지 배경 */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['gray_100']} 0%, {COLORS['gray_200']} 100%);
    }}

    /* 폼 스타일링 */
    .login-box {{
        background: {COLORS['card_bg']};
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07), 0 12px 28px rgba(0,0,0,0.07);
        padding: 2.5rem;
        max-width: 400px;
        margin: 0 auto;
    }}

    /* 입력 필드 아이콘 스타일 */
    .input-icon {{
        position: relative;
    }}

    .input-icon svg {{
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        color: {COLORS['gray_400']};
    }}

    .input-icon input {{
        padding-left: 40px;
    }}

    /* 가입 조건 박스 */
    .register-info {{
        background: {COLORS['gray_100']};
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        font-size: 0.8125rem;
        color: {COLORS['gray_600']};
    }}

    .register-info strong {{
        color: {COLORS['gray_700']};
    }}
    </style>
    """
