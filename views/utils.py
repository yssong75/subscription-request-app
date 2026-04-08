# -*- coding: utf-8 -*-
"""
pages/utils.py - 페이지 모듈 공통 유틸리티
"""

import streamlit as st
import calendar as _calendar
from datetime import date as _date


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
