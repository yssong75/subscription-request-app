# -*- coding: utf-8 -*-
"""
유틸리티 함수 모듈
"""

from datetime import datetime
import streamlit as st


def validate_email(email):
    """
    이메일 주소 유효성 검사

    Args:
        email (str): 이메일 주소

    Returns:
        bool: 유효 여부
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_datetime(dt=None):
    """
    현재 시각을 문자열로 포맷

    Args:
        dt (datetime, optional): 포맷할 datetime 객체. None이면 현재 시각 사용

    Returns:
        str: 포맷된 시각 문자열 (예: 2024-01-23 14:30:55)
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def init_session_state():
    """
    Streamlit session state 초기화
    """
    if 'selected_data' not in st.session_state:
        st.session_state.selected_data = None

    if 'request_data' not in st.session_state:
        st.session_state.request_data = None

    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "🔍 검색"

    if 'search_result' not in st.session_state:
        st.session_state.search_result = None

    if 'change_data' not in st.session_state:
        st.session_state.change_data = None

    if 'report_html' not in st.session_state:
        st.session_state.report_html = None

    if 'report_period' not in st.session_state:
        st.session_state.report_period = None

    if 'report_stats' not in st.session_state:
        st.session_state.report_stats = None

    if 'report_changes' not in st.session_state:
        st.session_state.report_changes = None

    if 'report_closures' not in st.session_state:
        st.session_state.report_closures = None

    # 본지점 변경관리
    if 'cm_search_result' not in st.session_state:
        st.session_state.cm_search_result = None

    # 본지점 폐쇄처리
    if 'cl_search_result' not in st.session_state:
        st.session_state.cl_search_result = None

    if 'cl_target' not in st.session_state:
        st.session_state.cl_target = None

    # 선불제 해지
    if 'pp_cl_result' not in st.session_state:
        st.session_state.pp_cl_result = None

    if 'pp_cl_target' not in st.session_state:
        st.session_state.pp_cl_target = None

    # 후불제 해지
    if 'pt_cl_result' not in st.session_state:
        st.session_state.pt_cl_result = None

    if 'pt_cl_target' not in st.session_state:
        st.session_state.pt_cl_target = None

    # 선불제 검색
    if 'pp_search_result' not in st.session_state:
        st.session_state.pp_search_result = None

    # 후불제 검색
    if 'pt_search_result' not in st.session_state:
        st.session_state.pt_search_result = None


def parse_email_from_display(display_str):
    """
    표시용 문자열에서 이메일 주소 추출

    Args:
        display_str (str): "홍길동<test@test.com>" 형식의 문자열

    Returns:
        str: 이메일 주소 (예: "test@test.com")
    """
    import re
    match = re.search(r'<(.+?)>', display_str)
    if match:
        return match.group(1)
    return display_str


def clear_request_data():
    """
    요청 데이터 초기화
    """
    st.session_state.selected_data = None
    st.session_state.request_data = None


def move_to_tab(tab_index):
    """
    특정 탭으로 이동

    Args:
        tab_index (int): 이동할 탭 인덱스 (0: 검색, 1: 청약작성, 2: 발송/이력)
    """
    st.session_state.active_tab = tab_index
