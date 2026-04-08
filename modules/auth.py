# -*- coding: utf-8 -*-
"""
인증 모듈 - 로그인/회원가입/세션 관리
"""

import streamlit as st
import bcrypt
import re
from datetime import datetime, timedelta

from db.adapter import get_user, register_user


# 보안 설정
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15
SESSION_TIMEOUT_MINUTES = 60


def hash_password(password):
    """비밀번호를 bcrypt로 해싱"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, hashed):
    """비밀번호 검증"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def validate_password_strength(password):
    """
    비밀번호 강도 검증
    - 최소 8자 이상
    - 영문자 포함
    - 숫자 포함
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"비밀번호는 최소 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다."
    if not re.search(r'[a-zA-Z]', password):
        return False, "비밀번호에 영문자가 포함되어야 합니다."
    if not re.search(r'\d', password):
        return False, "비밀번호에 숫자가 포함되어야 합니다."
    return True, ""


def validate_user_id(user_id):
    """
    아이디 유효성 검증
    - 4~20자
    - 영문, 숫자, 밑줄(_)만 허용
    - 영문으로 시작
    """
    if len(user_id) < 4 or len(user_id) > 20:
        return False, "아이디는 4~20자 사이여야 합니다."
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', user_id):
        return False, "아이디는 영문으로 시작하고, 영문/숫자/밑줄만 사용할 수 있습니다."
    return True, ""


def validate_email_format(email):
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "유효한 이메일 형식이 아닙니다."
    return True, ""


def check_login_lockout(user_id):
    """로그인 시도 횟수 확인 및 잠금 체크"""
    attempts_key = f'login_attempts_{user_id}'
    lockout_key = f'login_lockout_{user_id}'

    # 잠금 상태 확인
    if lockout_key in st.session_state:
        lockout_until = st.session_state[lockout_key]
        if datetime.now() < lockout_until:
            remaining = (lockout_until - datetime.now()).seconds // 60 + 1
            return False, f"로그인이 {remaining}분간 잠금되었습니다."
        else:
            # 잠금 해제
            del st.session_state[lockout_key]
            if attempts_key in st.session_state:
                del st.session_state[attempts_key]

    return True, ""


def record_login_attempt(user_id, success):
    """로그인 시도 기록"""
    attempts_key = f'login_attempts_{user_id}'
    lockout_key = f'login_lockout_{user_id}'

    if success:
        # 성공 시 시도 횟수 초기화
        if attempts_key in st.session_state:
            del st.session_state[attempts_key]
    else:
        # 실패 시 시도 횟수 증가
        if attempts_key not in st.session_state:
            st.session_state[attempts_key] = 0
        st.session_state[attempts_key] += 1

        # 최대 시도 횟수 초과 시 잠금
        if st.session_state[attempts_key] >= MAX_LOGIN_ATTEMPTS:
            st.session_state[lockout_key] = datetime.now() + timedelta(minutes=LOGIN_LOCKOUT_MINUTES)


def check_session_timeout():
    """세션 타임아웃 확인"""
    if 'last_activity' in st.session_state:
        last_activity = st.session_state.last_activity
        if datetime.now() - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            # 세션 만료
            logout()
            return True
    return False


def update_last_activity():
    """마지막 활동 시간 갱신"""
    st.session_state.last_activity = datetime.now()


def init_auth_state():
    """인증 관련 session_state 초기화"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "login"
    if 'just_registered' not in st.session_state:
        st.session_state.just_registered = False
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()


def is_authenticated():
    """인증 여부 확인 (세션 타임아웃 포함)"""
    if not st.session_state.get('authenticated', False):
        return False

    # 세션 타임아웃 체크
    if check_session_timeout():
        return False

    # 마지막 활동 시간 갱신
    update_last_activity()
    return True


def get_current_user():
    """현재 로그인된 사용자 정보 반환"""
    return st.session_state.get('user_info', None)


def logout():
    """로그아웃"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.auth_page = "login"
    if 'last_activity' in st.session_state:
        del st.session_state.last_activity


def show_login_page():
    """로그인/회원가입 페이지 표시 - Tabler 스타일"""
    init_auth_state()

    # Tabler Icons CDN + 스타일 CSS 적용
    st.markdown("""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
    <style>
    .ti { font-size: 1.25rem; vertical-align: middle; }
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    .login-card {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07), 0 12px 28px rgba(0,0,0,0.07);
        padding: 2.5rem 2rem;
        width: 100%;
        max-width: 480px;
        margin: 2rem auto;
        min-height: 200px;
    }
    .login-logo {
        width: 64px;
        height: 64px;
        background: linear-gradient(135deg, #066fd1 0%, #4263eb 100%);
        border-radius: 12px;
        margin: 0 auto 1.5rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .login-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.75rem;
        white-space: nowrap;
    }
    .login-subtitle {
        color: #64748b;
        font-size: 0.9375rem;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f1f5f9;
        border-radius: 6px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 4px;
        color: #64748b;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #066fd1 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem;
    }
    .stTextInput > label, .stSelectbox > label {
        color: #334155;
        font-weight: 500;
        font-size: 0.875rem;
    }
    /* ===== 입력 필드 통합 스타일 ===== */
    [data-baseweb="input"] {
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        background: #f1f5f9 !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-baseweb="input"]:focus-within {
        border-color: #066fd1 !important;
        box-shadow: 0 0 0 3px rgba(6,111,209,0.2) !important;
        background: #ffffff !important;
    }
    [data-baseweb="base-input"] {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    [data-baseweb="input"] input {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        background: transparent !important;
    }
    [data-baseweb="input"] button {
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        color: #64748b !important;
    }
    .stFormSubmitButton button {
        background: linear-gradient(135deg, #066fd1 0%, #4263eb 100%);
        border: none;
        border-radius: 6px;
        padding: 0.625rem 1rem;
        font-weight: 500;
        width: 100%;
    }
    .stFormSubmitButton button:hover {
        opacity: 0.9;
    }
    .register-tips {
        background: #f1f5f9;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
        font-size: 0.8125rem;
        color: #475569;
    }
    </style>
    """, unsafe_allow_html=True)

    # 회원가입 완료 후 로그인 탭으로 자동 전환 (JavaScript)
    if st.session_state.get('just_registered', False):
        st.markdown(
            """
            <script>
                setTimeout(function() {
                    const tabs = window.parent.document.querySelectorAll('button[data-baseweb="tab"]');
                    if (tabs.length > 0) {
                        tabs[0].click();
                    }
                }, 100);
            </script>
            """,
            unsafe_allow_html=True
        )

    # 중앙 정렬 레이아웃 - 더 넓은 중앙 영역
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            """
            <div class="login-card">
                <div class="login-logo"><i class="ti ti-file-text" style="color:white;font-size:1.75rem;"></i></div>
                <h1 class="login-title">KB 청약요청 시스템</h1>
                <p class="login-subtitle">계정에 로그인하세요</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 로그인 / 회원가입 전환
        tab_login, tab_register = st.tabs(["로그인", "회원가입"])

        with tab_login:
            _show_login_form()

        with tab_register:
            _show_register_form()


def _show_login_form():
    """로그인 폼"""
    # 회원가입 완료 후 메시지 표시
    if st.session_state.get('just_registered', False):
        st.success("회원가입이 완료되었습니다! 로그인해주세요.")
        st.session_state.just_registered = False

    with st.form("login_form"):
        login_id = st.text_input("아이디", placeholder="아이디를 입력하세요", key="login_id")
        login_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="login_pw")

        submitted = st.form_submit_button("로그인", type="primary", use_container_width=True)

        if submitted:
            if not login_id or not login_pw:
                st.error("아이디와 비밀번호를 입력해주세요.")
                return

            # 로그인 잠금 체크
            can_login, lockout_msg = check_login_lockout(login_id)
            if not can_login:
                st.error(lockout_msg)
                return

            user = get_user(login_id)

            if user is None:
                record_login_attempt(login_id, False)
                st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                return

            if user.get("상태", "") != "활성":
                st.error("비활성화된 계정입니다. 관리자에게 문의하세요.")
                return

            stored_hash = user.get("비밀번호", "")
            if not stored_hash or not verify_password(login_pw, stored_hash):
                record_login_attempt(login_id, False)
                st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                return

            # 로그인 성공
            record_login_attempt(login_id, True)
            st.session_state.authenticated = True
            st.session_state.last_activity = datetime.now()
            st.session_state.user_info = {
                "아이디": user.get("아이디", ""),
                "이름": user.get("이름", ""),
                "이메일": user.get("이메일", ""),
                "권한": user.get("권한", "user"),
            }
            st.rerun()


def _show_register_form():
    """회원가입 폼 - Tabler 스타일"""
    st.markdown(
        """
        <div class="register-tips">
            <strong style="color:#1e293b;"><i class="ti ti-clipboard-list"></i> 가입 조건</strong><br><br>
            <span style="color:#066fd1;"><i class="ti ti-point"></i></span> 아이디: 4~20자, 영문으로 시작, 영문/숫자/밑줄만 허용<br>
            <span style="color:#066fd1;"><i class="ti ti-point"></i></span> 비밀번호: 8자 이상, 영문+숫자 조합 필수
        </div>
        """,
        unsafe_allow_html=True
    )
    with st.form("register_form"):
        reg_id = st.text_input("아이디", placeholder="영문으로 시작, 4~20자", key="reg_id")
        reg_pw = st.text_input("비밀번호", type="password", placeholder="8자 이상, 영문+숫자 조합", key="reg_pw")
        reg_pw_confirm = st.text_input("비밀번호 확인", type="password", placeholder="비밀번호를 다시 입력하세요", key="reg_pw_confirm")
        reg_name = st.text_input("이름", placeholder="이름을 입력하세요", key="reg_name")
        reg_email = st.text_input("이메일", placeholder="이메일을 입력하세요", key="reg_email")

        submitted = st.form_submit_button("계정 만들기 →", type="primary", use_container_width=True)

        if submitted:
            # 검증
            if not reg_id or not reg_pw or not reg_name or not reg_email:
                st.error("모든 필드를 입력해주세요.")
                return

            # 아이디 유효성 검증
            id_valid, id_msg = validate_user_id(reg_id)
            if not id_valid:
                st.error(id_msg)
                return

            # 비밀번호 강도 검증
            pw_valid, pw_msg = validate_password_strength(reg_pw)
            if not pw_valid:
                st.error(pw_msg)
                return

            if reg_pw != reg_pw_confirm:
                st.error("비밀번호가 일치하지 않습니다.")
                return

            # 이메일 형식 검증
            email_valid, email_msg = validate_email_format(reg_email)
            if not email_valid:
                st.error(email_msg)
                return

            # 중복 검사
            existing = get_user(reg_id)
            if existing is not None:
                st.error("이미 사용 중인 아이디입니다.")
                return

            # 등록
            user_data = {
                "아이디": reg_id,
                "비밀번호": hash_password(reg_pw),
                "이름": reg_name,
                "이메일": reg_email,
                "권한": "user",
                "등록일": datetime.now().strftime('%Y-%m-%d'),
                "상태": "활성",
            }

            success = register_user(user_data)
            if success:
                # 회원가입 성공 - 로그인 탭으로 자동 전환
                st.session_state.just_registered = True
                st.rerun()
            else:
                st.error("회원가입에 실패했습니다. 다시 시도해주세요.")
