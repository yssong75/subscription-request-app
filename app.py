# -*- coding: utf-8 -*-
"""
KB 청약요청 시스템 - 메인 Streamlit 애플리케이션
Tabler Vertical Transparent Layout 스타일
"""

import streamlit as st

from modules.utils import init_session_state
from modules.auth import init_auth_state, is_authenticated, show_login_page, logout, get_current_user
from styles import get_main_css


# 페이지 설정
st.set_page_config(
    page_title="KB 청약요청 시스템",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state 초기화
init_session_state()
init_auth_state()

# 현재 메뉴 상태 초기화
if 'current_menu' not in st.session_state:
    st.session_state.current_menu = "본지점_검색"

# ==================== 인증 게이트 ====================
if not is_authenticated():
    show_login_page()
    st.stop()

# ==================== 인증 후 메인 앱 ====================

# Tabler Icons CDN + Vertical Transparent Layout 스타일
st.markdown(get_main_css(), unsafe_allow_html=True)


# ==================== 사이드바 (왼쪽 메뉴 - 트리 구조) ====================
with st.sidebar:
    # 로고/브랜드
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-logo"><i class="ti ti-file-text"></i></div>
        <span class="sidebar-brand-title">KB 회선관리</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 현재 메뉴가 속한 섹션 확인
    def get_current_section():
        menu = st.session_state.current_menu
        if menu.startswith("본지점") or menu in ("검색", "청약 작성", "발송/이력", "변경관리", "신규등록"):
            return "본지점"
        elif menu.startswith("선불제"):
            return "선불제"
        elif menu.startswith("후불제"):
            return "후불제"
        return None

    current_section = get_current_section()

    # --- 본지점 섹션 ---
    본지점_menus = [
        ("본지점_검색", "🔍", "지점 검색"),
        ("본지점_청약작성", "✏️", "청약 작성"),
        ("본지점_메일발송", "📧", "메일 발송"),
        ("본지점_변경관리", "🔄", "변경관리"),
        ("본지점_폐쇄처리", "🚫", "폐쇄처리"),
        ("본지점_신규등록", "📝", "신규등록"),
    ]
    with st.expander("🏢 본지점", expanded=(current_section == "본지점")):
        for menu_key, icon_emoji, label in 본지점_menus:
            is_active = st.session_state.current_menu == menu_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{icon_emoji} {label}", key=f"menu_{menu_key}", use_container_width=True, type=btn_type):
                st.session_state.current_menu = menu_key
                st.rerun()

    # --- 선불제 섹션 ---
    선불제_menus = [
        ("선불제_검색", "🔍", "검색"),
        ("선불제_신규등록", "📝", "신규등록"),
        ("선불제_해지등록", "🗑️", "해지등록"),
    ]
    with st.expander("📡 선불제", expanded=(current_section == "선불제")):
        for menu_key, icon_emoji, label in 선불제_menus:
            is_active = st.session_state.current_menu == menu_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{icon_emoji} {label}", key=f"menu_{menu_key}", use_container_width=True, type=btn_type):
                st.session_state.current_menu = menu_key
                st.rerun()

    # --- 후불제 섹션 ---
    후불제_menus = [
        ("후불제_검색", "🔍", "검색"),
        ("후불제_신규등록", "📝", "신규등록"),
        ("후불제_해지등록", "🗑️", "해지등록"),
    ]
    with st.expander("📶 후불제", expanded=(current_section == "후불제")):
        for menu_key, icon_emoji, label in 후불제_menus:
            is_active = st.session_state.current_menu == menu_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{icon_emoji} {label}", key=f"menu_{menu_key}", use_container_width=True, type=btn_type):
                st.session_state.current_menu = menu_key
                st.rerun()

    st.markdown("---")

    # --- 공통 메뉴 ---
    공통_menus = [
        ("월별 레포트", "📊", "월별 레포트"),
        ("마이페이지", "👤", "마이페이지"),
    ]
    for menu_key, icon_emoji, label in 공통_menus:
        is_active = st.session_state.current_menu == menu_key
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon_emoji} {label}", key=f"menu_{menu_key}", use_container_width=True, type=btn_type):
            st.session_state.current_menu = menu_key
            st.rerun()

    st.markdown("---")

    # 사용자 정보
    user = get_current_user()
    user_initial = user['이름'][0] if user['이름'] else 'U'
    user_role = user.get('권한', 'user')
    role_display = "관리자" if user_role == "admin" else "사용자"

    st.markdown(f"""
    <div class="user-box">
        <div class="user-avatar">{user_initial}</div>
        <div class="user-details">
            <div class="user-name">{user['이름']}</div>
            <div class="user-role">{role_display}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 로그아웃 버튼
    st.markdown('<div class="logout-button">', unsafe_allow_html=True)
    if st.button("로그아웃", key="btn_logout", use_container_width=True):
        logout()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== 메인 콘텐츠 영역 ====================
current_menu = st.session_state.current_menu

# 페이지 헤더
menu_info = {
    # 본지점
    "본지점_검색": ("본지점", "지점 검색", "ti-search"),
    "본지점_청약작성": ("본지점", "청약 작성", "ti-edit"),
    "본지점_메일발송": ("본지점", "메일 발송 및 이력", "ti-mail"),
    "본지점_변경관리": ("본지점", "변경관리", "ti-refresh"),
    "본지점_폐쇄처리": ("본지점", "폐쇄처리", "ti-ban"),
    "본지점_신규등록": ("본지점", "신규등록", "ti-file-plus"),
    # 선불제
    "선불제_검색": ("선불제", "회선 검색", "ti-search"),
    "선불제_신규등록": ("선불제", "신규등록", "ti-file-plus"),
    "선불제_해지등록": ("선불제", "해지등록", "ti-file-minus"),
    # 후불제
    "후불제_검색": ("후불제", "회선 검색", "ti-search"),
    "후불제_신규등록": ("후불제", "신규등록", "ti-file-plus"),
    "후불제_해지등록": ("후불제", "해지등록", "ti-file-minus"),
    # 공통
    "월별 레포트": ("REPORT", "월별 레포트", "ti-chart-bar"),
    "마이페이지": ("PROFILE", "마이페이지", "ti-user"),
    # 하위 호환 (기존 메뉴 키)
    "검색": ("본지점", "지점 검색", "ti-search"),
    "청약 작성": ("본지점", "청약 작성", "ti-edit"),
    "발송/이력": ("본지점", "메일 발송 및 이력", "ti-mail"),
    "변경관리": ("본지점", "변경관리", "ti-refresh"),
    "신규등록": ("본지점", "신규등록", "ti-file-plus"),
}

pretitle, title, icon = menu_info.get(current_menu, ("", current_menu, "ti-home"))

st.markdown(f"""
<div class="page-header">
    <div class="page-pretitle">{pretitle}</div>
    <h2 class="page-title"><i class="ti {icon}" style="color:#066fd1;"></i> {title}</h2>
</div>
""", unsafe_allow_html=True)



# ==================== 페이지 라우팅 ====================
from views.branch  import (
    show_branch_search, show_branch_subscription, show_branch_mail,
    show_branch_change, show_branch_new, show_branch_closure,
)
from views.section import (
    show_prepaid_search, show_prepaid_new, show_prepaid_cancel,
    show_postpaid_search, show_postpaid_new, show_postpaid_cancel,
)
from views.report  import show_report
from views.mypage  import show_mypage

# 본지점
if current_menu in ("검색", "본지점_검색"):
    show_branch_search()
elif current_menu in ("청약 작성", "본지점_청약작성"):
    show_branch_subscription()
elif current_menu in ("발송/이력", "본지점_메일발송"):
    show_branch_mail()
elif current_menu in ("변경관리", "본지점_변경관리"):
    show_branch_change()
elif current_menu in ("신규등록", "본지점_신규등록"):
    show_branch_new()
elif current_menu == "본지점_폐쇄처리":
    show_branch_closure()

# 선불제
elif current_menu == "선불제_검색":
    show_prepaid_search()
elif current_menu == "선불제_신규등록":
    show_prepaid_new()
elif current_menu == "선불제_해지등록":
    show_prepaid_cancel()

# 후불제
elif current_menu == "후불제_검색":
    show_postpaid_search()
elif current_menu == "후불제_신규등록":
    show_postpaid_new()
elif current_menu == "후불제_해지등록":
    show_postpaid_cancel()

# 공통
elif current_menu == "월별 레포트":
    show_report()
elif current_menu == "마이페이지":
    show_mypage()


# 푸터
st.markdown("---")
st.markdown('<div style="text-align:center;color:#64748b;font-size:12px;">KB 회선관리 시스템 v2.0 | Powered by Streamlit</div>', unsafe_allow_html=True)
