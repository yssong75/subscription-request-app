# -*- coding: utf-8 -*-
"""
pages/branch.py - 본지점 관련 페이지 모듈
(검색, 청약작성, 메일발송, 변경관리, 신규등록, 폐쇄처리)
"""

import streamlit as st
from streamlit.components.v1 import html as st_html
import pandas as pd

from config import WORK_TYPES, WORK_TIMES, BRANCH_TYPES
from db.adapter import (
    search_data, save_request, get_logs, generate_request_id,
    get_mailing_list, update_data_row, close_branch,
    generate_change_summary, add_data_row, save_unified_log,
    get_rows_by_점번,
)
from modules.gmail import send_email, create_email_html
from modules.utils import validate_email, format_datetime, parse_email_from_display
from views.utils import korean_date_input


def show_branch_search():
    """본지점 검색 페이지 (lines 232~277)"""
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


def show_branch_subscription():
    """청약 작성 페이지 (lines 280~430)"""
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


def show_branch_mail():
    """메일 발송/이력 페이지 (lines 432~557)"""
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


def show_branch_change():
    """변경관리 페이지 (lines 559~716)"""
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


def show_branch_new():
    """신규등록 페이지 (lines 718~814)"""
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


def show_branch_closure():
    """본지점 폐쇄처리 페이지 (lines 817~887)"""
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
