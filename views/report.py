# -*- coding: utf-8 -*-
"""
pages/report.py - 월별 레포트 페이지
"""

import streamlit as st
from streamlit.components.v1 import html as st_html
import pandas as pd
from datetime import datetime

from db.adapter import (
    get_all_data_stats, get_monthly_changes, get_closure_stats,
    get_section_stats, get_mailing_list,
)
from modules.gmail import send_email, create_report_html
from modules.utils import validate_email, parse_email_from_display


def show_report():
    """월별 레포트 페이지"""
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

        total_all = sum(s.get("total", 0) for s in rpt_sections.values()) if rpt_sections else rpt_stats['total_count']
        closed_all = sum(s.get("closed", 0) for s in rpt_sections.values()) if rpt_sections else rpt_closures['total_closed']

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("전체 회선수", f"{total_all:,}개")
        m2.metric("운용 회선", f"{total_all - closed_all:,}개")
        m3.metric("폐쇄/해지", f"{closed_all:,}개")
        m4.metric("월간 변동", f"{rpt_changes['total_changes']:,}건")

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
