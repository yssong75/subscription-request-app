# -*- coding: utf-8 -*-
"""
pages/mypage.py - 마이페이지 (프로필/비밀번호 변경)
"""

import streamlit as st

from db.adapter import get_user, update_user
from modules.auth import (
    get_current_user, hash_password, verify_password,
    validate_password_strength,
)


def show_mypage():
    """마이페이지"""
    st.markdown("회원 정보를 확인하고 수정할 수 있습니다.")

    current_user = get_current_user()
    user_id = current_user.get("아이디", "")
    user_info = get_user(user_id)

    if user_info is None:
        st.error("사용자 정보를 불러올 수 없습니다.")
        return

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
