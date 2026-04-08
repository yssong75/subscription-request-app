# -*- coding: utf-8 -*-
"""
pages/section.py - 선불제 + 후불제 관련 페이지 모듈
(선불제 검색, 신규등록, 해지등록 / 후불제 검색, 신규등록, 해지등록)
"""

import streamlit as st
import pandas as pd

from config import (
    PREPAID_USAGE_TYPES, PREPAID_SERVICE_NAMES, PREPAID_RATE_PLANS,
    POSTPAID_CATEGORIES, POSTPAID_SERVICE_NAMES, POSTPAID_RATE_PLANS,
)
from db.adapter import (
    search_section_data, add_section_row, close_section_row,
    save_unified_log,
)
from views.utils import korean_date_input


def show_prepaid_search():
    """선불제 검색 페이지 (lines 889~941)"""
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


def show_prepaid_new():
    """선불제 신규등록 페이지 (lines 943~1013)"""
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


def show_prepaid_cancel():
    """선불제 해지등록 페이지 (lines 1016~1080)"""
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


def show_postpaid_search():
    """후불제 검색 페이지 (lines 1083~1141)"""
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


def show_postpaid_new():
    """후불제 신규등록 페이지 (lines 1144~1217)"""
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


def show_postpaid_cancel():
    """후불제 해지등록 페이지 (lines 1220~1284)"""
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
