# -*- coding: utf-8 -*-
"""
Supabase 클라이언트 싱글톤
앱 전역에서 단일 클라이언트 인스턴스를 공유합니다.
"""
import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase() -> Client:
    """
    Supabase 클라이언트 반환 (앱 생애주기 동안 1회 생성).
    secrets.toml 의 [supabase] 섹션을 사용합니다.
    """
    cfg = st.secrets.get("supabase", {})
    url = cfg.get("url", "")
    # service_role_key 로 RLS 우회 (모든 테이블 ENABLE ROW LEVEL SECURITY)
    key = cfg.get("service_role_key", "") or cfg.get("anon_key", "")

    if not url or not key:
        st.error("secrets.toml 에 [supabase] url / anon_key 가 설정되지 않았습니다.")
        raise RuntimeError("Supabase 설정 누락")

    return create_client(url, key)
