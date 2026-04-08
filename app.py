# -*- coding: utf-8 -*-
"""
KB 청약요청 시스템 - 메인 Streamlit 애플리케이션
Tabler Vertical Transparent Layout 스타일
"""

import streamlit as st
from streamlit.components.v1 import html as st_html
import pandas as pd
import calendar as _calendar
from datetime import datetime, date as _date


def korean_date_input(label, key, default=None):
    """한국식 날짜 입력 (년/월/일 셀렉트박스)"""
    if default is None:
        default = _date.today()
    today = _date.today()
    months_kr = ["1월", "2월", "3월", "4월", "5월", "6월",
                 "7월", "8월", "9월", "10월", "11월", "12월"]
    st.markdown(f"<p style='margin-bottom:4px;font-size:14px;'>{label}</p>", unsafe_allow_html=True)
    col_y, col_m, col_d = st.columns(3)
    with col_y:
        year = st.selectbox("년", range(today.year - 1, today.year + 3),
                            index=default.year - (today.year - 1),
                            key=f"{key}_year", label_visibility="collapsed")
        st.markdown("<p style='text-align:center;margin-top:-12px;font-size:12px;color:#888;'>년</p>", unsafe_allow_html=True)
    with col_m:
        month = st.selectbox("월", months_kr,
                             index=default.month - 1,
                             key=f"{key}_month", label_visibility="collapsed")
        month_num = months_kr.index(month) + 1
        st.markdown("<p style='text-align:center;margin-top:-12px;font-size:12px;color:#888;'>월</p>", unsafe_allow_html=True)
    with col_d:
        max_day = _calendar.monthrange(year, month_num)[1]
        day_val = min(default.day, max_day)
        day = st.selectbox("일", range(1, max_day + 1),
                           index=day_val - 1,
                           key=f"{key}_day", label_visibility="collapsed")
        st.markdown("<p style='text-align:center;margin-top:-12px;font-size:12px;color:#888;'>일</p>", unsafe_allow_html=True)
    return _date(year, month_num, day)

from config import WORK_TYPES, WORK_TIMES, BRANCH_TYPES, SECTIONS, PREPAID_USAGE_TYPES, PREPAID_SERVICE_NAMES, PREPAID_RATE_PLANS, POSTPAID_CATEGORIES, POSTPAID_SERVICE_NAMES, POSTPAID_RATE_PLANS
from modules.gsheet import search_data, save_request, get_logs, generate_request_id, get_mailing_list, update_data_row, close_branch, generate_change_summary, add_data_row, get_all_data_stats, get_monthly_changes, get_closure_stats, update_user, get_user, get_section_data, search_section_data, add_section_row, close_section_row, get_section_stats, save_unified_log, get_rows_by_점번
from modules.gmail import send_email, create_email_html, create_report_html
from modules.utils import validate_email, format_datetime, init_session_state, parse_email_from_display
from modules.auth import init_auth_state, is_authenticated, show_login_page, logout, get_current_user, hash_password, verify_password, validate_password_strength
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


# ==================== 검색 페이지 (본지점) ====================
if current_menu in ("검색", "본지점_검색"):
    st.markdown("점번 또는 지점명으로 검색하세요.")

    col1, col2 = st.columns([3, 1])

    with col1:
        search_keyword = st.text_input(
            "검색어 입력",
            placeholder="점번 또는 지점명을 입력하세요",
            key="search_keyword"
        )

    with col2:
        st.write("")
        st.write("")
        search_button = st.button("검색", key="btn_search", use_container_width=True)

    # 검색 실행
    if search_button:
        if not search_keyword or search_keyword.strip() == "":
            st.warning("검색어를 입력해주세요.")
        else:
            with st.spinner("검색 중..."):
                result_df = search_data(search_keyword)
                st.session_state.search_result = result_df

    # 검색 결과 표시
    if st.session_state.search_result is not None and not st.session_state.search_result.empty:
        result_df = st.session_state.search_result

        st.success(f"총 {len(result_df)}개의 결과를 찾았습니다.")
        st.dataframe(result_df, use_container_width=True)

        st.markdown('<div class="section-title"><i class="ti ti-hand-click" style="color:#066fd1;"></i> 선택</div>', unsafe_allow_html=True)
        for idx, row in result_df.iterrows():
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.text(f"점번: {row['점번']} | 지점명: {row['지점명']}")
            with col_btn:
                if st.button("선택", key=f"select_{idx}"):
                    st.session_state.selected_data = row.to_dict()
                    st.session_state.current_menu = "본지점_청약작성"
                    st.rerun()
    elif search_button and (st.session_state.search_result is None or st.session_state.search_result.empty):
        st.info("검색 결과가 없습니다.")


# ==================== 청약 작성 페이지 ====================
elif current_menu in ("청약 작성", "본지점_청약작성"):
    if st.session_state.selected_data is None:
        st.warning("먼저 '검색' 메뉴에서 지점을 선택해주세요.")
        st.info("왼쪽 '검색' 메뉴로 이동하여 점번이나 지점명을 검색하고 선택하세요.")
    else:
        selected = st.session_state.selected_data

        st.success(f"선택된 지점: **{selected.get('지점명', '')}** (점번: {selected.get('점번', '')})")

        # 기본 정보
        st.markdown('<div class="section-title"><i class="ti ti-pin" style="color:#066fd1;"></i> 기본 정보 (자동 입력)</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.text_input("점번", value=selected.get('점번', ''), disabled=True, key="info_점번")
            st.text_input("점포구분", value=selected.get('점포구분', ''), disabled=True, key="info_점포구분")
            st.text_input("전용회선", value=selected.get('전용회선', ''), disabled=True, key="info_전용회선")
            st.text_input("속도", value=selected.get('속도', ''), disabled=True, key="info_속도")

        with col2:
            st.text_input("지점명", value=selected.get('지점명', ''), disabled=True, key="info_지점명")
            st.text_input("Vlan ID", value=selected.get('Vlan ID', ''), disabled=True, key="vlan_display")
            st.text_input("비즈광랜", value=selected.get('비즈광랜', ''), disabled=True, key="biz_display")
            st.text_input("AP수", value=selected.get('AP수', ''), disabled=True, key="info_AP수")

        st.text_input("상위국", value=selected.get('상위국', ''), disabled=True, key="info_상위국")
        st.text_input("변경 전 주소", value=selected.get('주소1', ''), disabled=True, key="addr_before_display")

        # 본부부서: 망분리 회선 자동 탐색
        _망분리_전용회선_auto = ""
        _망분리_속도_auto = ""
        if selected.get('점포구분') == '본부부서':
            _같은점번_rows = get_rows_by_점번(selected.get('점번', ''))
            if not _같은점번_rows.empty and len(_같은점번_rows) > 1:
                _current_회선 = str(selected.get('전용회선', '')).strip()
                _other = _같은점번_rows[_같은점번_rows['전용회선'].astype(str).str.strip() != _current_회선]
                if not _other.empty:
                    _망분리_전용회선_auto = _other.iloc[0].get('전용회선', '')
                    _망분리_속도_auto = _other.iloc[0].get('속도', '')

            st.markdown('<div class="section-title"><i class="ti ti-network" style="color:#EC4899;"></i> 망분리 회선 (수정 가능)</div>', unsafe_allow_html=True)
            mb_col1, mb_col2 = st.columns(2)
            with mb_col1:
                망분리_전용회선 = st.text_input("망분리 전용회선 번호", value=_망분리_전용회선_auto, placeholder="없으면 공백", key="mb_전용회선")
            with mb_col2:
                망분리_속도 = st.text_input("망분리 속도", value=_망분리_속도_auto, placeholder="예: 100M", key="mb_속도")
        else:
            망분리_전용회선 = ""
            망분리_속도 = ""

        # 작업 정보 입력
        st.markdown('<div class="section-title"><i class="ti ti-writing" style="color:#066fd1;"></i> 작업 정보 입력</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            작업구분 = st.selectbox("작업 구분", options=WORK_TYPES)
            요청일 = korean_date_input("작업 요청일", key="요청일")
            담당자 = st.text_input("현장 담당자")
            거리층 = st.text_input("이동 거리/층", placeholder="예: 3층 → 5층")

        with col4:
            작업시간 = st.selectbox("작업 시간", options=WORK_TIMES)
            전화번호 = st.text_input("전화번호", placeholder="예: 010-1234-5678")
            요청사항 = st.text_area("요청 사항", placeholder="추가 요청사항을 입력하세요", height=100)

        # 층내이전/층간이전은 동일 건물 작업이므로 변경후주소 불필요
        _hide_addr = 작업구분 in ["층내이전", "층간이전"]
        if not _hide_addr:
            변경후주소 = st.text_input("변경 후 주소", placeholder="변경될 주소를 입력하세요")
        else:
            변경후주소 = ""

        # 메일 추가 내용
        st.markdown('<div class="section-title"><i class="ti ti-mail" style="color:#066fd1;"></i> 메일 추가 내용</div>', unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        with col5:
            메일인사말 = st.text_area("인사말 (메일 상단)", placeholder="안녕하세요.\n네트워크 장비 이전 관련하여 청약 요청드립니다.", height=100)
        with col6:
            메일서명 = st.text_area("추가 서명 (선택사항)", placeholder="담당자: 홍길동\n부서: IT운영팀", height=100)

        # 버튼
        st.markdown("---")
        col_preview, col_clear = st.columns([1, 1])

        is_exception = 작업구분 in ["폐쇄", "신규", "감속", "증속"]
        is_same_building = 작업구분 in ["층내이전", "층간이전"]

        with col_preview:
            if st.button("발송 미리보기", use_container_width=True, type="primary"):
                if not is_exception and not is_same_building:
                    if not 변경후주소:
                        st.error("변경 후 주소를 입력해주세요.")
                        st.stop()
                    if not 담당자:
                        st.error("현장 담당자를 입력해주세요.")
                        st.stop()
                    if not 전화번호:
                        st.error("전화번호를 입력해주세요.")
                        st.stop()

                if is_same_building:
                    # 동일 건물 이전 - 주소 변경 없음, 기존 주소 유지
                    변경후주소 = selected.get('주소1', '')
                    담당자 = 담당자 if 담당자 else "0"
                    전화번호 = 전화번호 if 전화번호 else "0"
                    거리층 = 거리층 if 거리층 else "0"
                    요청사항 = 요청사항 if 요청사항 else "0"

                if is_exception:
                    변경후주소 = 변경후주소 if 변경후주소 else "0"
                    담당자 = 담당자 if 담당자 else "0"
                    전화번호 = 전화번호 if 전화번호 else "0"
                    거리층 = 거리층 if 거리층 else "0"
                    요청사항 = 요청사항 if 요청사항 else "0"

                request_data = {
                    "점번": selected.get('점번', ''),
                    "지점명": selected.get('지점명', ''),
                    "점포구분": selected.get('점포구분', ''),
                    "전용회선": selected.get('전용회선', ''),
                    "Vlan ID": selected.get('Vlan ID', ''),
                    "비즈광랜": selected.get('비즈광랜', ''),
                    "속도": selected.get('속도', ''),
                    "AP수": selected.get('AP수', ''),
                    "상위국": selected.get('상위국', ''),
                    "변경전주소": selected.get('주소1', ''),
                    "변경후주소": 변경후주소,
                    "작업구분": 작업구분,
                    "요청일": str(요청일),
                    "작업시간": 작업시간,
                    "담당자": 담당자,
                    "전화번호": 전화번호,
                    "요청사항": 요청사항,
                    "거리층": 거리층,
                    "메일인사말": 메일인사말,
                    "메일서명": 메일서명,
                    "망분리_전용회선": 망분리_전용회선,
                    "망분리_속도": 망분리_속도,
                }

                st.session_state.request_data = request_data
                st.session_state.current_menu = "본지점_메일발송"
                st.rerun()

        with col_clear:
            if st.button("입력 초기화", use_container_width=True):
                st.session_state.selected_data = None
                st.session_state.request_data = None
                st.session_state.search_result = None
                st.rerun()


# ==================== 발송/이력 페이지 ====================
elif current_menu in ("발송/이력", "본지점_메일발송"):
    if st.session_state.request_data is None:
        st.warning("먼저 '청약 작성' 메뉴에서 청약을 작성해주세요.")
    else:
        request_data = st.session_state.request_data

        # 청약 수정 버튼 (청약 작성 단계로 복귀, request_data 유지)
        if st.button("← 청약 수정", key="btn_back_to_draft"):
            st.session_state.current_menu = "본지점_청약작성"
            st.rerun()

        st.markdown('<div class="section-title"><i class="ti ti-mail-forward" style="color:#066fd1;"></i> 메일 본문 미리보기</div>', unsafe_allow_html=True)
        html_body = create_email_html(request_data)
        st_html(html_body, height=800, scrolling=True)

        st.markdown("---")

        st.markdown('<div class="section-title"><i class="ti ti-users" style="color:#066fd1;"></i> 수신자 설정</div>', unsafe_allow_html=True)
        mailing_options = get_mailing_list()

        col_to, col_cc, col_bcc = st.columns(3)
        with col_to:
            selected_to = st.multiselect("수신자 (TO)", options=mailing_options, key="mail_to")
        with col_cc:
            selected_cc = st.multiselect("참조 (CC)", options=mailing_options, key="mail_cc")
        with col_bcc:
            selected_bcc = st.multiselect("비밀참조 (BCC)", options=mailing_options, key="mail_bcc")

        email_subject = st.text_input("메일 제목", value=f"[청약요청] {request_data.get('지점명', '')} - {request_data.get('작업구분', '')}")

        if st.button("메일 발송", use_container_width=True, type="primary"):
            email_list = [parse_email_from_display(s) for s in selected_to]
            cc_list = [parse_email_from_display(s) for s in selected_cc]
            bcc_list = [parse_email_from_display(s) for s in selected_bcc]

            all_emails = email_list + cc_list + bcc_list
            invalid_emails = [email for email in all_emails if not validate_email(email)]

            if not email_list:
                st.error("수신자(TO)를 1명 이상 선택해주세요.")
            elif invalid_emails:
                st.error(f"유효하지 않은 이메일 주소: {', '.join(invalid_emails)}")
            else:
                with st.spinner("메일 발송 중..."):
                    send_success = send_email(email_list, email_subject, html_body, cc_emails=cc_list, bcc_emails=bcc_list)

                    if send_success:
                        request_id = generate_request_id()
                        발송시각 = format_datetime()

                        save_data = {
                            "요청ID": request_id,
                            "점번": request_data.get('점번', ''),
                            "지점명": request_data.get('지점명', ''),
                            "전용회선": request_data.get('전용회선', ''),
                            "Vlan ID": request_data.get('Vlan ID', ''),
                            "비즈광랜": request_data.get('비즈광랜', ''),
                            "속도": request_data.get('속도', ''),
                            "AP수": request_data.get('AP수', ''),
                            "상위국": request_data.get('상위국', ''),
                            "변경전주소": request_data.get('변경전주소', ''),
                            "변경후주소": request_data.get('변경후주소', ''),
                            "작업구분": request_data.get('작업구분', ''),
                            "요청일": request_data.get('요청일', ''),
                            "작업시간": request_data.get('작업시간', ''),
                            "담당자": request_data.get('담당자', ''),
                            "전화번호": request_data.get('전화번호', ''),
                            "요청사항": request_data.get('요청사항', ''),
                            "거리층": request_data.get('거리층', ''),
                            "발송여부": "Y",
                            "발송시각": 발송시각,
                            "수신자": f"TO:{', '.join(email_list)}" + (f" | CC:{', '.join(cc_list)}" if cc_list else "") + (f" | BCC:{', '.join(bcc_list)}" if bcc_list else "")
                        }

                        save_request(save_data)

                        log_data = {
                            "변경시각": 발송시각,
                            "점번": request_data.get('점번', ''),
                            "지점명": request_data.get('지점명', ''),
                            "이전주소": request_data.get('변경전주소', ''),
                            "신규주소": request_data.get('변경후주소', ''),
                            "요청일": request_data.get('요청일', ''),
                            "작업시간": request_data.get('작업시간', ''),
                            "작업구분": request_data.get('작업구분', '')
                        }
                        save_unified_log("본지점", log_data)

                        # DATA 시트 자동 업데이트
                        _작업구분 = request_data.get('작업구분', '')
                        _변경후주소 = request_data.get('변경후주소', '')
                        _변경전주소 = request_data.get('변경전주소', '')

                        # 주소지이전만 주소1 업데이트
                        # (층내이전/층간이전은 동일 건물 작업 - 주소 변경 없음)
                        if _작업구분 in ['주소지이전']:
                            if _변경후주소 and _변경후주소 != _변경전주소:
                                update_result = update_data_row(
                                    request_data.get('점번'),
                                    {"주소1": _변경후주소}
                                )
                                if update_result:
                                    st.info("📝 DATA 시트가 자동 업데이트되었습니다. (주소1 → 변경후주소)")

                        st.success(f"메일이 성공적으로 발송되었습니다! (요청ID: {request_id})")
                        st.balloons()

                        # 세션 초기화 (변경관리로 자동 이동 없음)
                        st.session_state.selected_data = None
                        st.session_state.request_data = None
                        st.session_state.search_result = None
                    else:
                        st.error("메일 발송에 실패했습니다. 다시 시도해주세요.")

    # 발송 이력
    st.markdown("---")
    st.markdown('<div class="section-title"><i class="ti ti-history" style="color:#066fd1;"></i> 최근 발송 이력</div>', unsafe_allow_html=True)

    with st.spinner("이력 조회 중..."):
        logs_df = get_logs(limit=20)
        if logs_df.empty:
            st.info("발송 이력이 없습니다.")
        else:
            st.dataframe(logs_df, use_container_width=True)


# ==================== 변경관리 페이지 ====================
elif current_menu in ("변경관리", "본지점_변경관리"):
    st.markdown("지점 정보를 검색하여 직접 수정합니다.")

    # 편집 모드가 아닐 때: 검색 UI
    if st.session_state.change_data is None:
        st.markdown('<div class="section-title"><i class="ti ti-search" style="color:#066fd1;"></i> 변경 대상 검색</div>', unsafe_allow_html=True)
        cm_col1, cm_col2 = st.columns([3, 1])

        with cm_col1:
            cm_keyword = st.text_input("검색어 입력", placeholder="점번 또는 지점명을 입력하세요", key="cm_keyword")
        with cm_col2:
            st.write("")
            st.write("")
            cm_search_btn = st.button("검색", key="btn_cm_search", use_container_width=True)

        if cm_search_btn and cm_keyword and cm_keyword.strip():
            with st.spinner("검색 중..."):
                cm_result = search_data(cm_keyword)
                st.session_state.cm_search_result = cm_result

        if st.session_state.get("cm_search_result") is not None and not st.session_state.get("cm_search_result", pd.DataFrame()).empty:
            cm_df = st.session_state.cm_search_result
            st.success(f"총 {len(cm_df)}개의 결과를 찾았습니다.")
            st.dataframe(cm_df, use_container_width=True)

            st.markdown('<div class="section-title"><i class="ti ti-edit" style="color:#066fd1;"></i> 수정할 지점 선택</div>', unsafe_allow_html=True)
            for idx, row in cm_df.iterrows():
                col_info, col_btn = st.columns([5, 1])
                with col_info:
                    st.text(f"점번: {row['점번']} | 지점명: {row['지점명']} | 주소: {row.get('주소1', '')[:30]}...")
                with col_btn:
                    if st.button("수정", key=f"cm_edit_{idx}"):
                        # change_data 세션에 원본 데이터 저장
                        st.session_state.change_data = {
                            "점번": row.get('점번', ''),
                            "지점명": row.get('지점명', ''),
                            "점포구분": row.get('점포구분', ''),
                            "전용회선": row.get('전용회선', ''),
                            "Vlan ID": row.get('Vlan ID', ''),
                            "비즈광랜": row.get('비즈광랜', ''),
                            "속도": row.get('속도', ''),
                            "AP수": row.get('AP수', ''),
                            "상위국": row.get('상위국', ''),
                            "주소1": row.get('주소1', ''),
                            "작업구분": "변경",
                            "_원본_지점명": row.get('지점명', ''),
                            "_원본_점포구분": row.get('점포구분', ''),
                            "_원본_전용회선": row.get('전용회선', ''),
                            "_원본_Vlan ID": row.get('Vlan ID', ''),
                            "_원본_비즈광랜": row.get('비즈광랜', ''),
                            "_원본_속도": row.get('속도', ''),
                            "_원본_AP수": row.get('AP수', ''),
                            "_원본_상위국": row.get('상위국', ''),
                            "_원본_주소1": row.get('주소1', ''),
                        }
                        st.rerun()

        elif cm_search_btn:
            st.info("검색 결과가 없습니다.")

    # 편집 모드: 수정 폼
    else:
        cd = st.session_state.change_data
        작업구분_cd = cd.get('작업구분', '변경')

        st.success(f"수정 대상: **{cd.get('지점명', '')}** (점번: {cd.get('점번', '')})")

        st.markdown('<div class="section-title"><i class="ti ti-table" style="color:#066fd1;"></i> 지점 정보 수정</div>', unsafe_allow_html=True)
        st.markdown("수정이 필요한 필드를 변경한 후 저장 버튼을 눌러주세요.")

        col1, col2 = st.columns(2)
        with col1:
            cm_점번 = st.text_input("점번", value=cd.get('점번', ''), disabled=True, key="cm_점번")
            _current_branch = cd.get('점포구분', '영업점')
            _branch_idx = BRANCH_TYPES.index(_current_branch) if _current_branch in BRANCH_TYPES else 0
            cm_점포구분 = st.selectbox("점포구분", options=BRANCH_TYPES, index=_branch_idx, key="cm_점포구분")
            cm_전용회선 = st.text_input("전용회선", value=cd.get('전용회선', ''), key="cm_전용회선")
            cm_Vlan_ID = st.text_input("Vlan ID", value=cd.get('Vlan ID', ''), key="cm_Vlan_ID")
            cm_속도 = st.text_input("속도", value=cd.get('속도', ''), key="cm_속도")
            cm_상위국 = st.text_input("상위국", value=cd.get('상위국', ''), key="cm_상위국")

        with col2:
            cm_지점명 = st.text_input("지점명", value=cd.get('지점명', ''), key="cm_지점명")
            cm_비즈광랜 = st.text_input("비즈광랜", value=cd.get('비즈광랜', ''), key="cm_비즈광랜")
            cm_AP수 = st.text_input("AP수", value=cd.get('AP수', ''), key="cm_AP수")

        cm_주소1 = st.text_input("주소1", value=cd.get('주소1', ''), key="cm_주소1")

        st.markdown("---")
        col_save, col_cancel = st.columns([1, 1])

        with col_save:
            if st.button("저장", use_container_width=True, type="primary"):
                with st.spinner("저장 중..."):
                    점번 = cd.get('점번', '')

                    updated = {
                        "지점명": cm_지점명,
                        "점포구분": cm_점포구분,
                        "전용회선": cm_전용회선,
                        "Vlan ID": cm_Vlan_ID,
                        "비즈광랜": cm_비즈광랜,
                        "속도": cm_속도,
                        "AP수": cm_AP수,
                        "상위국": cm_상위국,
                        "주소1": cm_주소1,
                    }

                    original = {
                        "지점명": cd.get('_원본_지점명', ''),
                        "점포구분": cd.get('_원본_점포구분', ''),
                        "전용회선": cd.get('_원본_전용회선', ''),
                        "Vlan ID": cd.get('_원본_Vlan ID', ''),
                        "비즈광랜": cd.get('_원본_비즈광랜', ''),
                        "속도": cd.get('_원본_속도', ''),
                        "AP수": cd.get('_원본_AP수', ''),
                        "상위국": cd.get('_원본_상위국', ''),
                        "주소1": cd.get('_원본_주소1', ''),
                    }

                    changes = {}
                    for key in updated:
                        if str(updated[key]).strip() != str(original[key]).strip():
                            changes[key] = updated[key]

                    if not changes:
                        st.info("변경된 내용이 없습니다.")
                    else:
                        success = update_data_row(점번, changes)
                        if success:
                            summary = generate_change_summary(original, updated)
                            log_data = {
                                "변경시각": format_datetime(),
                                "점번": 점번,
                                "지점명": cm_지점명,
                                "전용회선": cm_전용회선,
                                "비즈광랜": cm_비즈광랜,
                                "이전주소": cd.get('_원본_주소1', ''),
                                "신규주소": cm_주소1,
                                "요청일": "",
                                "작업시간": "",
                                "작업구분": "변경",
                                "변경 요약": summary
                            }
                            save_unified_log("본지점", log_data)
                            st.success(f"DATA 시트가 업데이트되었습니다. ({summary})")
                            st.session_state.change_data = None
                            st.session_state.cm_search_result = None
                            st.rerun()
                        else:
                            st.error("DATA 시트 업데이트에 실패했습니다.")

        with col_cancel:
            if st.button("취소", use_container_width=True):
                st.session_state.change_data = None
                st.rerun()


# ==================== 신규등록 페이지 ====================
elif current_menu in ("신규등록", "본지점_신규등록"):
    st.markdown("새로운 지점을 DATA 시트에 직접 등록합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-pin" style="color:#066fd1;"></i> 기본 정보 입력</div>', unsafe_allow_html=True)
    nr_col1, nr_col2 = st.columns(2)

    with nr_col1:
        nr_점번 = st.text_input("점번", placeholder="점번을 입력하세요", key="nr_점번")
        nr_점포구분 = st.selectbox("점포구분", options=BRANCH_TYPES, key="nr_점포구분")
        nr_전용회선 = st.text_input("전용회선", placeholder="전용회선 번호 (없으면 공백)", key="nr_전용회선")
        nr_Vlan_ID = st.text_input("Vlan ID", value="1004", key="nr_Vlan_ID")
        nr_속도 = st.text_input("속도", placeholder="예: 100M", key="nr_속도")

    with nr_col2:
        nr_지점명 = st.text_input("지점명", placeholder="지점명을 입력하세요", key="nr_지점명")
        nr_비즈광랜 = st.text_input("비즈광랜", placeholder="비즈광랜 번호 (없으면 공백)", key="nr_비즈광랜")
        nr_AP수 = st.text_input("AP수", placeholder="예: 2", key="nr_AP수")

    nr_주소1 = st.text_input("주소", placeholder="주소를 입력하세요", key="nr_주소1")
    nr_상위국 = st.text_input("상위국", placeholder="상위국을 입력하세요", key="nr_상위국")

    # 본부부서: 망분리 회선 (전용회선과 동일 구조, 별도 행으로 저장)
    if nr_점포구분 == "본부부서":
        st.markdown('<div class="section-title"><i class="ti ti-network" style="color:#066fd1;"></i> 망분리 회선 (해당 시 입력)</div>', unsafe_allow_html=True)
        mb_col1, mb_col2 = st.columns(2)
        with mb_col1:
            nr_망분리_번호 = st.text_input("망분리 전용회선 번호", placeholder="없으면 공백", key="nr_망분리_번호")
        with mb_col2:
            nr_망분리_속도 = st.text_input("망분리 속도", placeholder="예: 100M", key="nr_망분리_속도")
    else:
        nr_망분리_번호 = ""
        nr_망분리_속도 = ""

    st.markdown("---")
    nr_col_save, nr_col_cancel = st.columns([1, 1])

    with nr_col_save:
        if st.button("저장", use_container_width=True, type="primary", key="nr_save"):
            if not nr_점번:
                st.error("점번을 입력해주세요.")
            elif not nr_지점명:
                st.error("지점명을 입력해주세요.")
            else:
                with st.spinner("저장 중..."):
                    new_data = {
                        "점번": nr_점번,
                        "지점명": nr_지점명,
                        "점포구분": nr_점포구분,
                        "전용회선": nr_전용회선,
                        "Vlan ID": nr_Vlan_ID,
                        "비즈광랜": nr_비즈광랜,
                        "속도": nr_속도,
                        "AP수": nr_AP수,
                        "주소1": nr_주소1,
                        "상위국": nr_상위국,
                        "사용여부": "Y",
                    }

                    success = add_data_row(new_data)
                    # 망분리 회선이 있으면 동일 점번으로 별도 행 저장
                    if success and nr_망분리_번호.strip():
                        망분리_data = {
                            "점번": nr_점번,
                            "지점명": nr_지점명,
                            "점포구분": nr_점포구분,
                            "전용회선": nr_망분리_번호,
                            "Vlan ID": nr_Vlan_ID,
                            "비즈광랜": "",
                            "속도": nr_망분리_속도,
                            "AP수": "",
                            "주소1": nr_주소1,
                            "상위국": nr_상위국,
                            "사용여부": "Y",
                        }
                        add_data_row(망분리_data)

                    if success:
                        log_data = {
                            "변경시각": format_datetime(),
                            "점번": nr_점번,
                            "지점명": nr_지점명,
                            "이전주소": "",
                            "신규주소": nr_주소1,
                            "요청일": "",
                            "작업시간": "",
                            "작업구분": "신규",
                            "변경 요약": "#신규 등록" + (" (망분리 포함)" if nr_망분리_번호.strip() else "")
                        }
                        save_unified_log("본지점", log_data)
                        st.success(f"신규 지점이 등록되었습니다! (점번: {nr_점번}, 지점명: {nr_지점명})" + (f" 망분리 회선도 등록됨." if nr_망분리_번호.strip() else ""))
                    else:
                        st.error("신규 등록에 실패했습니다.")

    with nr_col_cancel:
        if st.button("취소", use_container_width=True, key="nr_cancel"):
            st.rerun()


# ==================== 본지점 폐쇄처리 페이지 ====================
elif current_menu == "본지점_폐쇄처리":
    st.markdown("지점을 검색하여 폐쇄 처리합니다. DATA → 폐쇄관리 시트로 이동됩니다.")

    st.markdown('<div class="section-title"><i class="ti ti-search" style="color:#066fd1;"></i> 폐쇄 대상 검색</div>', unsafe_allow_html=True)
    cl_col1, cl_col2 = st.columns([3, 1])

    with cl_col1:
        cl_keyword = st.text_input("검색어 입력", placeholder="점번 또는 지점명을 입력하세요", key="cl_keyword")
    with cl_col2:
        st.write("")
        st.write("")
        cl_search_btn = st.button("검색", key="btn_cl_search", use_container_width=True)

    if cl_search_btn and cl_keyword and cl_keyword.strip():
        with st.spinner("검색 중..."):
            cl_result = search_data(cl_keyword)
            st.session_state.cl_search_result = cl_result

    if st.session_state.get("cl_search_result") is not None and not st.session_state.cl_search_result.empty:
        cl_df = st.session_state.cl_search_result
        st.success(f"총 {len(cl_df)}개의 결과를 찾았습니다.")
        st.dataframe(cl_df, use_container_width=True)

        st.markdown('<div class="section-title"><i class="ti ti-ban" style="color:#DC2626;"></i> 폐쇄 처리</div>', unsafe_allow_html=True)
        for idx, row in cl_df.iterrows():
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.text(f"점번: {row['점번']} | 지점명: {row['지점명']} | 전용회선: {row.get('전용회선', '')}")
            with col_btn:
                if st.button("폐쇄", key=f"close_{idx}", type="secondary"):
                    st.session_state.cl_target = row.to_dict()

        if st.session_state.get("cl_target"):
            target = st.session_state.cl_target
            st.warning(f"**{target['지점명']}** (점번: {target['점번']})을(를) 폐쇄 처리하시겠습니까?")
            cl_date = korean_date_input("폐쇄 일자", key="cl_date")
            cl_confirm_col1, cl_confirm_col2 = st.columns(2)
            with cl_confirm_col1:
                if st.button("폐쇄 확인", use_container_width=True, type="primary", key="cl_confirm"):
                    with st.spinner("폐쇄 처리 중..."):
                        success = close_branch(target['점번'])
                        if success:
                            log_data = {
                                "변경시각": format_datetime(),
                                "점번": target['점번'],
                                "지점명": target['지점명'],
                                "전용회선": target.get('전용회선', ''),
                                "비즈광랜": target.get('비즈광랜', ''),
                                "이전주소": target.get('주소1', ''),
                                "신규주소": "",
                                "요청일": str(cl_date),
                                "작업시간": "",
                                "작업구분": "폐쇄",
                                "변경 요약": "#폐쇄 처리"
                            }
                            save_unified_log("본지점", log_data)
                            st.success(f"**{target['지점명']}** 폐쇄 처리가 완료되었습니다.")
                            st.session_state.cl_target = None
                            st.session_state.cl_search_result = None
                            st.rerun()
                        else:
                            st.error("폐쇄 처리에 실패했습니다.")
            with cl_confirm_col2:
                if st.button("취소", use_container_width=True, key="cl_cancel"):
                    st.session_state.cl_target = None
                    st.rerun()

    elif cl_search_btn:
        st.info("검색 결과가 없습니다.")


# ==================== 선불제 검색 페이지 ====================
elif current_menu == "선불제_검색":
    st.markdown("서비스번호 또는 지점명으로 선불제 회선을 검색합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-search" style="color:#0F9B8E;"></i> 선불제 회선 검색</div>', unsafe_allow_html=True)
    pp_s_col1, pp_s_col2 = st.columns([3, 1])

    with pp_s_col1:
        pp_s_keyword = st.text_input("검색어 입력", placeholder="서비스번호 또는 지점명을 입력하세요", key="pp_s_keyword")
    with pp_s_col2:
        st.write("")
        st.write("")
        pp_s_search = st.button("검색", key="btn_pp_s_search", use_container_width=True)

    if pp_s_search and pp_s_keyword and pp_s_keyword.strip():
        with st.spinner("검색 중..."):
            pp_s_result = search_section_data("선불제", pp_s_keyword)
            st.session_state.pp_search_result = pp_s_result

    if st.session_state.get("pp_search_result") is not None and not st.session_state.get("pp_search_result", pd.DataFrame()).empty:
        pp_s_df = st.session_state.pp_search_result
        st.success(f"총 {len(pp_s_df)}개의 결과를 찾았습니다.")

        # 주요 컬럼 표시
        display_cols = [c for c in ["서비스번호", "서비스명", "요금제", "용도", "상위국", "지점명", "하위국주소", "속도", "비용", "계약일", "상태"] if c in pp_s_df.columns]
        st.dataframe(pp_s_df[display_cols] if display_cols else pp_s_df, use_container_width=True)

        # 상세 보기
        st.markdown('<div class="section-title"><i class="ti ti-info-circle" style="color:#0F9B8E;"></i> 상세 정보</div>', unsafe_allow_html=True)
        for idx, row in pp_s_df.iterrows():
            with st.expander(f"📡 {row.get('지점명', '')} ({row.get('서비스번호', '')})"):
                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.markdown(f"**서비스번호:** {row.get('서비스번호', '')}")
                    st.markdown(f"**서비스명:** {row.get('서비스명', '')}")
                    st.markdown(f"**요금제:** {row.get('요금제', '')}")
                    st.markdown(f"**용도:** {row.get('용도', '')}")
                    st.markdown(f"**상위국:** {row.get('상위국', '')}")
                    st.markdown(f"**상위주소:** {row.get('상위주소', '')}")
                with detail_col2:
                    st.markdown(f"**지점명:** {row.get('지점명', '')}")
                    st.markdown(f"**하위국주소:** {row.get('하위국주소', '')}")
                    st.markdown(f"**속도:** {row.get('속도', '')}")
                    st.markdown(f"**비용:** {row.get('비용', '')}")
                    st.markdown(f"**계약일:** {row.get('계약일', '')}")
                    st.markdown(f"**약정기간:** {row.get('약정기간', '')}")
                st.markdown(f"**장비명:** {row.get('장비명', '')} | **동작방식:** {row.get('동작방식', '')}")
                st.markdown(f"**비고:** {row.get('비고', '')}")
                st.markdown(f"**상태:** {row.get('상태', '')}")

    elif pp_s_search:
        st.info("검색 결과가 없습니다.")


# ==================== 선불제 신규등록 페이지 ====================
elif current_menu == "선불제_신규등록":
    st.markdown("선불제 회선을 신규 등록합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-file-plus" style="color:#0F9B8E;"></i> 선불제 회선 정보 입력</div>', unsafe_allow_html=True)

    pp_col1, pp_col2 = st.columns(2)
    with pp_col1:
        pp_서비스번호 = st.text_input("서비스번호", placeholder="서비스번호를 입력하세요", key="pp_서비스번호")
        pp_서비스명 = st.selectbox("서비스명", options=PREPAID_SERVICE_NAMES, key="pp_서비스명")
        pp_요금제 = st.selectbox("요금제", options=PREPAID_RATE_PLANS, key="pp_요금제")
        pp_용도 = st.selectbox("용도", options=PREPAID_USAGE_TYPES, key="pp_용도")
        pp_상위국 = st.text_input("상위국", placeholder="상위국", key="pp_상위국")
        pp_상위주소 = st.text_input("상위주소", placeholder="상위주소", key="pp_상위주소")
        pp_장비명 = st.text_input("장비명", placeholder="장비명", key="pp_장비명")
        pp_동작방식 = st.text_input("동작방식", placeholder="동작방식", key="pp_동작방식")

    with pp_col2:
        pp_지점명 = st.text_input("지점명", placeholder="지점명 (하위국)", key="pp_지점명")
        pp_하위국주소 = st.text_input("하위국 주소", placeholder="하위국 주소", key="pp_하위국주소")
        pp_속도 = st.text_input("속도", placeholder="예: 100M", key="pp_속도")
        pp_비용 = st.text_input("비용", placeholder="월 비용", key="pp_비용")
        pp_계약일 = korean_date_input("계약일", key="pp_계약일")
        pp_약정기간 = st.text_input("약정기간", placeholder="예: 3년", key="pp_약정기간")
        pp_비고 = st.text_area("비고", placeholder="비고사항", height=68, key="pp_비고")

    st.markdown("---")
    pp_save_col, pp_cancel_col = st.columns(2)

    with pp_save_col:
        if st.button("저장", use_container_width=True, type="primary", key="pp_save"):
            if not pp_서비스번호:
                st.error("서비스번호를 입력해주세요.")
            elif not pp_지점명:
                st.error("지점명을 입력해주세요.")
            else:
                with st.spinner("저장 중..."):
                    new_data = {
                        "번호": "",
                        "서비스번호": pp_서비스번호,
                        "서비스명": pp_서비스명,
                        "요금제": pp_요금제,
                        "용도": pp_용도,
                        "상위국": pp_상위국,
                        "상위주소": pp_상위주소,
                        "지점명": pp_지점명,
                        "하위국주소": pp_하위국주소,
                        "속도": pp_속도,
                        "비용": pp_비용,
                        "계약일": str(pp_계약일),
                        "약정기간": pp_약정기간,
                        "장비명": pp_장비명,
                        "동작방식": pp_동작방식,
                        "비고": pp_비고,
                        "상태": "운용",
                    }
                    success = add_section_row("선불제", new_data)
                    if success:
                        save_unified_log("선불제", {
                            "점번": pp_서비스번호,
                            "지점명": pp_지점명,
                            "작업구분": "신규",
                            "변경 요약": "#선불제 신규 등록"
                        })
                        st.success(f"선불제 회선이 등록되었습니다! (서비스번호: {pp_서비스번호})")
                    else:
                        st.error("등록에 실패했습니다.")

    with pp_cancel_col:
        if st.button("취소", use_container_width=True, key="pp_cancel"):
            st.rerun()


# ==================== 선불제 해지등록 페이지 ====================
elif current_menu == "선불제_해지등록":
    st.markdown("선불제 회선을 검색하여 해지 처리합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-search" style="color:#0F9B8E;"></i> 해지 대상 검색</div>', unsafe_allow_html=True)
    pp_cl_col1, pp_cl_col2 = st.columns([3, 1])

    with pp_cl_col1:
        pp_cl_keyword = st.text_input("검색어 입력", placeholder="서비스번호 또는 지점명", key="pp_cl_keyword")
    with pp_cl_col2:
        st.write("")
        st.write("")
        pp_cl_search = st.button("검색", key="btn_pp_cl_search", use_container_width=True)

    if pp_cl_search and pp_cl_keyword and pp_cl_keyword.strip():
        with st.spinner("검색 중..."):
            pp_cl_result = search_section_data("선불제", pp_cl_keyword)
            st.session_state.pp_cl_result = pp_cl_result

    if st.session_state.get("pp_cl_result") is not None and not st.session_state.get("pp_cl_result", pd.DataFrame()).empty:
        pp_cl_df = st.session_state.pp_cl_result
        st.success(f"총 {len(pp_cl_df)}개의 결과를 찾았습니다.")

        # 주요 컬럼만 표시
        display_cols = [c for c in ["서비스번호", "서비스명", "용도", "지점명", "하위국주소", "속도", "상태"] if c in pp_cl_df.columns]
        st.dataframe(pp_cl_df[display_cols] if display_cols else pp_cl_df, use_container_width=True)

        st.markdown('<div class="section-title"><i class="ti ti-file-minus" style="color:#DC2626;"></i> 해지 처리</div>', unsafe_allow_html=True)
        for idx, row in pp_cl_df.iterrows():
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.text(f"서비스번호: {row.get('서비스번호', '')} | 지점명: {row.get('지점명', '')} | 용도: {row.get('용도', '')}")
            with col_btn:
                if st.button("해지", key=f"pp_close_{idx}", type="secondary"):
                    st.session_state.pp_cl_target = row.to_dict()

        if st.session_state.get("pp_cl_target"):
            target = st.session_state.pp_cl_target
            st.warning(f"**{target.get('지점명', '')}** (서비스번호: {target.get('서비스번호', '')})을(를) 해지 처리하시겠습니까?")
            pp_cl_date = korean_date_input("해지 일자", key="pp_cl_date")
            pp_conf_col1, pp_conf_col2 = st.columns(2)
            with pp_conf_col1:
                if st.button("해지 확인", use_container_width=True, type="primary", key="pp_cl_confirm"):
                    with st.spinner("해지 처리 중..."):
                        success = close_section_row("선불제", target.get("서비스번호", ""), str(pp_cl_date))
                        if success:
                            save_unified_log("선불제", {
                                "점번": target.get("서비스번호", ""),
                                "지점명": target.get("지점명", ""),
                                "작업구분": "해지",
                                "변경 요약": "#선불제 해지"
                            })
                            st.success(f"**{target.get('지점명', '')}** 해지 처리가 완료되었습니다.")
                            st.session_state.pp_cl_target = None
                            st.session_state.pp_cl_result = None
                            st.rerun()
                        else:
                            st.error("해지 처리에 실패했습니다.")
            with pp_conf_col2:
                if st.button("취소", use_container_width=True, key="pp_cl_cancel"):
                    st.session_state.pp_cl_target = None
                    st.rerun()

    elif pp_cl_search:
        st.info("검색 결과가 없습니다.")


# ==================== 후불제 검색 페이지 ====================
elif current_menu == "후불제_검색":
    st.markdown("서비스번호 또는 지점명으로 후불제 회선을 검색합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-search" style="color:#8B5CF6;"></i> 후불제 회선 검색</div>', unsafe_allow_html=True)
    pt_s_col1, pt_s_col2 = st.columns([3, 1])

    with pt_s_col1:
        pt_s_keyword = st.text_input("검색어 입력", placeholder="서비스번호 또는 지점명을 입력하세요", key="pt_s_keyword")
    with pt_s_col2:
        st.write("")
        st.write("")
        pt_s_search = st.button("검색", key="btn_pt_s_search", use_container_width=True)

    if pt_s_search and pt_s_keyword and pt_s_keyword.strip():
        with st.spinner("검색 중..."):
            pt_s_result = search_section_data("후불제", pt_s_keyword)
            st.session_state.pt_search_result = pt_s_result

    if st.session_state.get("pt_search_result") is not None and not st.session_state.get("pt_search_result", pd.DataFrame()).empty:
        pt_s_df = st.session_state.pt_search_result
        st.success(f"총 {len(pt_s_df)}개의 결과를 찾았습니다.")

        # 구분별 필터
        구분_list = ["전체"] + list(pt_s_df["구분"].dropna().unique()) if "구분" in pt_s_df.columns else ["전체"]
        selected_구분 = st.selectbox("구분 필터", options=구분_list, key="pt_s_filter")

        filtered_df = pt_s_df if selected_구분 == "전체" else pt_s_df[pt_s_df["구분"] == selected_구분]

        # 주요 컬럼 표시
        display_cols = [c for c in ["서비스번호", "서비스명", "요금제", "구분", "지점명", "하위국주소", "속도", "요금", "계약일", "상태"] if c in filtered_df.columns]
        st.dataframe(filtered_df[display_cols] if display_cols else filtered_df, use_container_width=True)

        # 상세 보기
        st.markdown('<div class="section-title"><i class="ti ti-info-circle" style="color:#8B5CF6;"></i> 상세 정보</div>', unsafe_allow_html=True)
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📶 {row.get('지점명', '')} ({row.get('서비스번호', '')}) - {row.get('구분', '')}"):
                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.markdown(f"**서비스번호:** {row.get('서비스번호', '')}")
                    st.markdown(f"**서비스명:** {row.get('서비스명', '')}")
                    st.markdown(f"**요금제:** {row.get('요금제', '')}")
                    st.markdown(f"**구분:** {row.get('구분', '')}")
                    st.markdown(f"**지점명:** {row.get('지점명', '')}")
                    st.markdown(f"**하위국주소:** {row.get('하위국주소', '')}")
                with detail_col2:
                    st.markdown(f"**속도:** {row.get('속도', '')}")
                    st.markdown(f"**요금:** {row.get('요금', '')}")
                    st.markdown(f"**계약일:** {row.get('계약일', '')}")
                    st.markdown(f"**약정기간:** {row.get('약정기간', '')}")
                    st.markdown(f"**장비명:** {row.get('장비명', '')}")
                    st.markdown(f"**WIFI수량:** {row.get('WIFI수량', '')}")
                if row.get('구분') == 'LTE':
                    st.markdown(f"**LTE번호:** {row.get('LTE번호', '')} | **코너명:** {row.get('코너명', '')}")
                st.markdown(f"**비고:** {row.get('비고', '')}")
                st.markdown(f"**상태:** {row.get('상태', '')}")

    elif pt_s_search:
        st.info("검색 결과가 없습니다.")


# ==================== 후불제 신규등록 페이지 ====================
elif current_menu == "후불제_신규등록":
    st.markdown("후불제 회선을 신규 등록합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-file-plus" style="color:#8B5CF6;"></i> 후불제 회선 정보 입력</div>', unsafe_allow_html=True)

    # 구분 선택 (영업점인터넷, LTE, 인뱅/국제)
    pt_구분 = st.selectbox("구분", options=POSTPAID_CATEGORIES, key="pt_구분")

    pt_col1, pt_col2 = st.columns(2)
    with pt_col1:
        pt_서비스번호 = st.text_input("서비스번호", placeholder="서비스번호를 입력하세요", key="pt_서비스번호")
        pt_서비스명 = st.selectbox("서비스명", options=POSTPAID_SERVICE_NAMES, key="pt_서비스명")
        pt_요금제 = st.selectbox("요금제", options=POSTPAID_RATE_PLANS, key="pt_요금제")
        pt_지점명 = st.text_input("지점명", placeholder="지점명", key="pt_지점명")
        pt_하위국주소 = st.text_input("하위국 주소", placeholder="하위국 주소", key="pt_하위국주소")
        pt_속도 = st.text_input("속도", placeholder="예: 100M", key="pt_속도")
        pt_장비명 = st.text_input("장비명", placeholder="장비명", key="pt_장비명")

    with pt_col2:
        pt_계약일 = korean_date_input("계약일", key="pt_계약일")
        pt_약정기간 = st.text_input("약정기간", placeholder="예: 3년", key="pt_약정기간")
        pt_WIFI수량 = st.text_input("WIFI수량", placeholder="WIFI 수량", key="pt_WIFI수량")
        pt_요금 = st.text_input("요금", placeholder="월 요금", key="pt_요금")
        pt_LTE번호 = st.text_input("LTE번호", placeholder="LTE 번호 (LTE 구분 시)", key="pt_LTE번호")
        pt_코너명 = st.text_input("코너명", placeholder="코너명 (LTE 구분 시)", key="pt_코너명")
        pt_비고 = st.text_area("비고", placeholder="비고사항", height=68, key="pt_비고")

    st.markdown("---")
    pt_save_col, pt_cancel_col = st.columns(2)

    with pt_save_col:
        if st.button("저장", use_container_width=True, type="primary", key="pt_save"):
            if not pt_서비스번호:
                st.error("서비스번호를 입력해주세요.")
            elif not pt_지점명:
                st.error("지점명을 입력해주세요.")
            else:
                with st.spinner("저장 중..."):
                    new_data = {
                        "번호": "",
                        "서비스번호": pt_서비스번호,
                        "서비스명": pt_서비스명,
                        "요금제": pt_요금제,
                        "구분": pt_구분,
                        "지점명": pt_지점명,
                        "하위국주소": pt_하위국주소,
                        "속도": pt_속도,
                        "계약일": str(pt_계약일),
                        "약정기간": pt_약정기간,
                        "장비명": pt_장비명,
                        "WIFI수량": pt_WIFI수량,
                        "요금": pt_요금,
                        "LTE번호": pt_LTE번호,
                        "코너명": pt_코너명,
                        "운영상태": "운용",
                        "비고": pt_비고,
                        "상태": "운용",
                    }
                    success = add_section_row("후불제", new_data)
                    if success:
                        save_unified_log("후불제", {
                            "점번": pt_서비스번호,
                            "지점명": pt_지점명,
                            "작업구분": "신규",
                            "변경 요약": f"#후불제 신규 등록 ({pt_구분})"
                        })
                        st.success(f"후불제 회선이 등록되었습니다! (서비스번호: {pt_서비스번호})")
                    else:
                        st.error("등록에 실패했습니다.")

    with pt_cancel_col:
        if st.button("취소", use_container_width=True, key="pt_cancel"):
            st.rerun()


# ==================== 후불제 해지등록 페이지 ====================
elif current_menu == "후불제_해지등록":
    st.markdown("후불제 회선을 검색하여 해지 처리합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-search" style="color:#8B5CF6;"></i> 해지 대상 검색</div>', unsafe_allow_html=True)
    pt_cl_col1, pt_cl_col2 = st.columns([3, 1])

    with pt_cl_col1:
        pt_cl_keyword = st.text_input("검색어 입력", placeholder="서비스번호 또는 지점명", key="pt_cl_keyword")
    with pt_cl_col2:
        st.write("")
        st.write("")
        pt_cl_search = st.button("검색", key="btn_pt_cl_search", use_container_width=True)

    if pt_cl_search and pt_cl_keyword and pt_cl_keyword.strip():
        with st.spinner("검색 중..."):
            pt_cl_result = search_section_data("후불제", pt_cl_keyword)
            st.session_state.pt_cl_result = pt_cl_result

    if st.session_state.get("pt_cl_result") is not None and not st.session_state.get("pt_cl_result", pd.DataFrame()).empty:
        pt_cl_df = st.session_state.pt_cl_result
        st.success(f"총 {len(pt_cl_df)}개의 결과를 찾았습니다.")

        # 주요 컬럼만 표시
        display_cols = [c for c in ["서비스번호", "서비스명", "구분", "지점명", "하위국주소", "속도", "상태"] if c in pt_cl_df.columns]
        st.dataframe(pt_cl_df[display_cols] if display_cols else pt_cl_df, use_container_width=True)

        st.markdown('<div class="section-title"><i class="ti ti-file-minus" style="color:#DC2626;"></i> 해지 처리</div>', unsafe_allow_html=True)
        for idx, row in pt_cl_df.iterrows():
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.text(f"서비스번호: {row.get('서비스번호', '')} | 지점명: {row.get('지점명', '')} | 구분: {row.get('구분', '')}")
            with col_btn:
                if st.button("해지", key=f"pt_close_{idx}", type="secondary"):
                    st.session_state.pt_cl_target = row.to_dict()

        if st.session_state.get("pt_cl_target"):
            target = st.session_state.pt_cl_target
            st.warning(f"**{target.get('지점명', '')}** (서비스번호: {target.get('서비스번호', '')})을(를) 해지 처리하시겠습니까?")
            pt_cl_date = korean_date_input("해지 일자", key="pt_cl_date")
            pt_conf_col1, pt_conf_col2 = st.columns(2)
            with pt_conf_col1:
                if st.button("해지 확인", use_container_width=True, type="primary", key="pt_cl_confirm"):
                    with st.spinner("해지 처리 중..."):
                        success = close_section_row("후불제", target.get("서비스번호", ""), str(pt_cl_date))
                        if success:
                            save_unified_log("후불제", {
                                "점번": target.get("서비스번호", ""),
                                "지점명": target.get("지점명", ""),
                                "작업구분": "해지",
                                "변경 요약": f"#후불제 해지 ({target.get('구분', '')})"
                            })
                            st.success(f"**{target.get('지점명', '')}** 해지 처리가 완료되었습니다.")
                            st.session_state.pt_cl_target = None
                            st.session_state.pt_cl_result = None
                            st.rerun()
                        else:
                            st.error("해지 처리에 실패했습니다.")
            with pt_conf_col2:
                if st.button("취소", use_container_width=True, key="pt_cl_cancel"):
                    st.session_state.pt_cl_target = None
                    st.rerun()

    elif pt_cl_search:
        st.info("검색 결과가 없습니다.")


# ==================== 월별 레포트 페이지 ====================
elif current_menu == "월별 레포트":
    st.markdown("월별 네트워크 회선 현황 및 변동이력 레포트를 생성하고 메일로 발송합니다.")

    st.markdown('<div class="section-title"><i class="ti ti-calendar" style="color:#066fd1;"></i> 레포트 기간 선택</div>', unsafe_allow_html=True)
    col_year, col_month, col_generate = st.columns([1, 1, 1])

    with col_year:
        report_year = st.selectbox("연도", options=list(range(datetime.now().year, datetime.now().year - 3, -1)), key="report_year")
    with col_month:
        report_month = st.selectbox("월", options=list(range(1, 13)), index=datetime.now().month - 1, key="report_month")
    with col_generate:
        st.write("")
        st.write("")
        generate_report = st.button("레포트 생성", use_container_width=True, type="primary")

    if generate_report:
        with st.spinner("데이터 수집 및 레포트 생성 중..."):
            stats = get_all_data_stats()
            changes = get_monthly_changes(report_year, report_month)
            closures = get_closure_stats()

            # 선불제/후불제 섹션 통계
            prepaid_stats = get_section_stats("선불제")
            postpaid_stats = get_section_stats("후불제")
            section_stats = {
                "본지점": {"total": stats["total_count"], "closed": closures["total_closed"]},
                "선불제": prepaid_stats,
                "후불제": postpaid_stats,
            }

            period_str = f"{report_year}년 {report_month}월"
            report_html = create_report_html(stats, changes, closures, period_str, section_stats=section_stats)

            st.session_state.report_html = report_html
            st.session_state.report_period = period_str
            st.session_state.report_stats = stats
            st.session_state.report_changes = changes
            st.session_state.report_closures = closures
            st.session_state.report_section_stats = section_stats

    if st.session_state.get("report_html"):
        st.markdown("---")

        st.markdown('<div class="section-title"><i class="ti ti-trending-up" style="color:#066fd1;"></i> 주요 지표</div>', unsafe_allow_html=True)
        rpt_stats = st.session_state.report_stats
        rpt_changes = st.session_state.report_changes
        rpt_closures = st.session_state.report_closures
        rpt_sections = st.session_state.get("report_section_stats", {})

        # 전체 합산 (본지점 + 선불제 + 후불제)
        total_all = sum(s.get("total", 0) for s in rpt_sections.values()) if rpt_sections else rpt_stats['total_count']
        closed_all = sum(s.get("closed", 0) for s in rpt_sections.values()) if rpt_sections else rpt_closures['total_closed']

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("전체 회선수", f"{total_all:,}개")
        m2.metric("운용 회선", f"{total_all - closed_all:,}개")
        m3.metric("폐쇄/해지", f"{closed_all:,}개")
        m4.metric("월간 변동", f"{rpt_changes['total_changes']:,}건")

        # 섹션별 카드
        if rpt_sections:
            st.markdown('<div class="section-title"><i class="ti ti-layout-grid" style="color:#066fd1;"></i> 섹션별 현황</div>', unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("🏢 본지점", f"{rpt_sections.get('본지점', {}).get('total', 0):,}개", f"폐쇄 {rpt_sections.get('본지점', {}).get('closed', 0):,}")
            sc2.metric("📡 선불제", f"{rpt_sections.get('선불제', {}).get('total', 0):,}개", f"해지 {rpt_sections.get('선불제', {}).get('closed', 0):,}")
            sc3.metric("📶 후불제", f"{rpt_sections.get('후불제', {}).get('total', 0):,}개", f"해지 {rpt_sections.get('후불제', {}).get('closed', 0):,}")

        st.markdown('<div class="section-title"><i class="ti ti-chart-pie" style="color:#066fd1;"></i> 본지점 점포구분별 현황</div>', unsafe_allow_html=True)
        branch_data = rpt_stats["by_branch_type"]
        branch_df = pd.DataFrame(list(branch_data.items()), columns=["점포구분", "회선수"])
        st.bar_chart(branch_df.set_index("점포구분"))

        st.markdown('<div class="section-title"><i class="ti ti-mail-forward" style="color:#066fd1;"></i> 메일 본문 미리보기</div>', unsafe_allow_html=True)
        st_html(st.session_state.report_html, height=800, scrolling=True)

        st.markdown("---")

        st.markdown('<div class="section-title"><i class="ti ti-users" style="color:#066fd1;"></i> 수신자 설정</div>', unsafe_allow_html=True)
        mailing_options_rpt = get_mailing_list()

        col_rpt_to, col_rpt_cc, col_rpt_bcc = st.columns(3)
        with col_rpt_to:
            rpt_to = st.multiselect("수신자 (TO)", options=mailing_options_rpt, key="rpt_mail_to")
        with col_rpt_cc:
            rpt_cc = st.multiselect("참조 (CC)", options=mailing_options_rpt, key="rpt_mail_cc")
        with col_rpt_bcc:
            rpt_bcc = st.multiselect("비밀참조 (BCC)", options=mailing_options_rpt, key="rpt_mail_bcc")

        rpt_subject = st.text_input("메일 제목", value=f"[월별 레포트] {st.session_state.report_period} 네트워크 회선 현황", key="rpt_subject")

        if st.button("레포트 발송", use_container_width=True, type="primary", key="rpt_send"):
            email_list = [parse_email_from_display(s) for s in rpt_to]
            cc_list = [parse_email_from_display(s) for s in rpt_cc]
            bcc_list = [parse_email_from_display(s) for s in rpt_bcc]

            all_emails = email_list + cc_list + bcc_list
            invalid_emails = [e for e in all_emails if not validate_email(e)]

            if not email_list:
                st.error("수신자(TO)를 1명 이상 선택해주세요.")
            elif invalid_emails:
                st.error(f"유효하지 않은 이메일 주소: {', '.join(invalid_emails)}")
            else:
                with st.spinner("레포트 메일 발송 중..."):
                    success = send_email(email_list, rpt_subject, st.session_state.report_html, cc_emails=cc_list, bcc_emails=bcc_list)
                    if success:
                        st.success("레포트가 성공적으로 발송되었습니다!")
                    else:
                        st.error("레포트 발송에 실패했습니다.")


# ==================== 마이페이지 ====================
elif current_menu == "마이페이지":
    st.markdown("회원 정보를 확인하고 수정할 수 있습니다.")

    current_user = get_current_user()
    user_id = current_user.get("아이디", "")
    user_info = get_user(user_id)

    if user_info is None:
        st.error("사용자 정보를 불러올 수 없습니다.")
    else:
        st.markdown('<div class="section-title"><i class="ti ti-id" style="color:#066fd1;"></i> 기본 정보</div>', unsafe_allow_html=True)
        mp_col1, mp_col2 = st.columns(2)

        with mp_col1:
            st.text_input("아이디", value=user_info.get("아이디", ""), disabled=True, key="mp_id")
            mp_name = st.text_input("이름", value=user_info.get("이름", ""), key="mp_name")

        with mp_col2:
            st.text_input("권한", value=user_info.get("권한", "user"), disabled=True, key="mp_role")
            mp_email = st.text_input("이메일", value=user_info.get("이메일", ""), key="mp_email")

        st.text_input("등록일", value=user_info.get("등록일", ""), disabled=True, key="mp_regdate")

        if st.button("기본 정보 저장", key="mp_save_info"):
            if not mp_name.strip():
                st.error("이름을 입력해주세요.")
            elif not mp_email.strip():
                st.error("이메일을 입력해주세요.")
            else:
                updates = {}
                if mp_name.strip() != user_info.get("이름", ""):
                    updates["이름"] = mp_name.strip()
                if mp_email.strip() != user_info.get("이메일", ""):
                    updates["이메일"] = mp_email.strip()

                if not updates:
                    st.info("변경된 내용이 없습니다.")
                else:
                    success = update_user(user_id, updates)
                    if success:
                        if "이름" in updates:
                            st.session_state.user_info["이름"] = updates["이름"]
                        if "이메일" in updates:
                            st.session_state.user_info["이메일"] = updates["이메일"]
                        st.success("기본 정보가 저장되었습니다.")
                        st.rerun()
                    else:
                        st.error("정보 저장에 실패했습니다.")

        st.markdown("---")

        st.markdown('<div class="section-title"><i class="ti ti-lock" style="color:#066fd1;"></i> 비밀번호 변경</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#fffbeb;padding:10px 15px;border-radius:6px;margin-bottom:15px;font-size:12px;color:#92400e;border-left:4px solid #f59e0b;">비밀번호는 8자 이상, 영문+숫자 조합이 필수입니다.</div>', unsafe_allow_html=True)

        with st.form("password_change_form"):
            pw_current = st.text_input("현재 비밀번호", type="password", placeholder="현재 비밀번호를 입력하세요", key="pw_current")
            pw_new = st.text_input("새 비밀번호", type="password", placeholder="8자 이상, 영문+숫자 조합", key="pw_new")
            pw_confirm = st.text_input("새 비밀번호 확인", type="password", placeholder="새 비밀번호를 다시 입력하세요", key="pw_confirm")

            pw_submitted = st.form_submit_button("비밀번호 변경", type="primary", use_container_width=True)

            if pw_submitted:
                if not pw_current or not pw_new or not pw_confirm:
                    st.error("모든 필드를 입력해주세요.")
                else:
                    stored_hash = user_info.get("비밀번호", "")
                    if not verify_password(pw_current, stored_hash):
                        st.error("현재 비밀번호가 일치하지 않습니다.")
                    elif pw_new != pw_confirm:
                        st.error("새 비밀번호가 일치하지 않습니다.")
                    else:
                        pw_valid, pw_msg = validate_password_strength(pw_new)
                        if not pw_valid:
                            st.error(pw_msg)
                        else:
                            new_hash = hash_password(pw_new)
                            success = update_user(user_id, {"비밀번호": new_hash})
                            if success:
                                st.success("비밀번호가 변경되었습니다. 3초 후 로그인 페이지로 이동합니다.")
                                st.markdown('<script>setTimeout(function(){window.parent.location.reload();},3000);</script>', unsafe_allow_html=True)
                                st.session_state.authenticated = False
                                st.session_state.user_info = None
                            else:
                                st.error("비밀번호 변경에 실패했습니다.")


# 푸터
st.markdown("---")
st.markdown('<div style="text-align:center;color:#64748b;font-size:12px;">KB 회선관리 시스템 v2.0 | Powered by Streamlit</div>', unsafe_allow_html=True)
