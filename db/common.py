# -*- coding: utf-8 -*-
"""
공통 데이터 액세스 (Supabase)
- 사용자 관리
- 메일링 리스트
- 변경 로그
- 청약 요청
"""
import pandas as pd
import streamlit as st
from datetime import datetime

from db.client import get_supabase

_TTL = 300


# ══════════════════════════════════════════════════════════════════
# 사용자
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def _get_all_users() -> list[dict]:
    """사용자 전체 캐싱 (10분)"""
    try:
        sb = get_supabase()
        res = sb.table("users").select("*").execute()
        return res.data or []
    except Exception:
        return []


def get_user(user_id: str) -> dict | None:
    """아이디로 사용자 조회"""
    for u in _get_all_users():
        if u.get("아이디", "").strip() == user_id.strip():
            return u
    return None


def register_user(user_data: dict) -> bool:
    """신규 사용자 등록"""
    try:
        sb = get_supabase()
        row = {k: v for k, v in user_data.items() if k not in ("id", "등록일", "최근로그인", "수정일")}
        row.setdefault("권한", "일반")
        row.setdefault("상태", "활성")
        sb.table("users").insert(row).execute()
        _get_all_users.clear()
        return True
    except Exception as e:
        st.error(f"사용자 등록 실패: {str(e)}")
        return False


def update_user(user_id: str, updates: dict) -> bool:
    """사용자 정보 업데이트"""
    try:
        sb = get_supabase()
        clean = {k: v for k, v in updates.items() if k not in ("id", "등록일", "수정일")}
        sb.table("users").update(clean).eq("아이디", user_id).execute()
        _get_all_users.clear()
        return True
    except Exception as e:
        st.error(f"사용자 업데이트 실패: {str(e)}")
        return False


# ══════════════════════════════════════════════════════════════════
# 메일링 리스트
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=_TTL)
def get_mailing_list() -> list[str]:
    """
    메일링 리스트 조회 (5분 캐싱).
    반환: ["이름<email>", ...] 형식 (gsheet.py 와 동일)
    """
    try:
        sb = get_supabase()
        res = sb.table("mailing_list").select("이름, 이메일").execute()
        result = []
        for row in (res.data or []):
            name  = (row.get("이름") or "").strip()
            email = (row.get("이메일") or "").strip()
            if name and email:
                result.append(f"{name}<{email}>")
        return result
    except Exception as e:
        st.error(f"메일링 리스트 조회 실패: {str(e)}")
        return []


# ══════════════════════════════════════════════════════════════════
# 청약 요청
# ══════════════════════════════════════════════════════════════════

def save_request(data_dict: dict) -> bool:
    """청약 요청 저장"""
    try:
        sb = get_supabase()
        row = _clean_request(data_dict)
        sb.table("requests").upsert(row, on_conflict="요청id").execute()
        return True
    except Exception as e:
        st.error(f"청약요청 저장 실패: {str(e)}")
        return False


def get_requests(limit: int = 100) -> pd.DataFrame:
    """최근 청약 요청 조회"""
    try:
        sb = get_supabase()
        res = (sb.table("requests")
               .select("*")
               .order("등록일", desc=True)
               .limit(limit)
               .execute())
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"청약요청 조회 실패: {str(e)}")
        return pd.DataFrame()


def generate_request_id() -> str:
    """요청ID 생성 (REQ + 타임스탬프)"""
    return f"REQ{datetime.now().strftime('%Y%m%d%H%M%S')}"


def _clean_request(d: dict) -> dict:
    """청약 요청 dict 정리 (DB 컬럼명 맞춤)"""
    rename = {"Vlan ID": "vlan_id", "AP수": "ap수"}
    skip = {"id", "등록일", "수정일"}
    result = {}
    for k, v in d.items():
        if k in skip:
            continue
        db_k = rename.get(k, k)
        result[db_k] = str(v) if (v is not None and str(v).strip()) else None
    return result


# ══════════════════════════════════════════════════════════════════
# 변경 로그
# ══════════════════════════════════════════════════════════════════

def save_log(data_dict: dict) -> bool:
    """변경 로그 저장"""
    try:
        sb = get_supabase()
        row = {k: v for k, v in data_dict.items() if k not in ("id", "수정일")}
        row.setdefault("분류", "본지점")
        sb.table("change_logs").insert(row).execute()
        _get_all_logs.clear()
        get_monthly_changes.clear()
        return True
    except Exception as e:
        st.error(f"변경로그 저장 실패: {str(e)}")
        return False


def save_unified_log(data_dict: dict) -> bool:
    """통합 변경 로그 저장 (save_log 래퍼)"""
    return save_log(data_dict)


@st.cache_data(ttl=_TTL)
def _get_all_logs() -> pd.DataFrame:
    """변경로그 전체 캐싱 (5분)"""
    try:
        sb = get_supabase()
        res = sb.table("change_logs").select("*").order("등록일", desc=True).execute()
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=_TTL)
def get_monthly_changes(year: int, month: int) -> dict:
    """월별 변경로그 조회"""
    try:
        df = _get_all_logs()
        if df.empty:
            return {"total_changes": 0, "by_work_type": {}, "changes_list": pd.DataFrame()}

        df["_dt"] = pd.to_datetime(df["등록일"], errors="coerce")
        mask = (df["_dt"].dt.year == year) & (df["_dt"].dt.month == month)
        filtered = df[mask].drop(columns=["_dt"])
        by_work = filtered["작업구분"].value_counts().to_dict() if "작업구분" in filtered.columns else {}
        return {"total_changes": len(filtered), "by_work_type": by_work, "changes_list": filtered}
    except Exception as e:
        st.error(f"월별 변경로그 조회 실패: {str(e)}")
        return {"total_changes": 0, "by_work_type": {}, "changes_list": pd.DataFrame()}


def get_logs(limit: int = 50) -> pd.DataFrame:
    """최근 변경로그 조회"""
    try:
        sb = get_supabase()
        res = (sb.table("change_logs")
               .select("*")
               .order("등록일", desc=True)
               .limit(limit)
               .execute())
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"변경로그 조회 실패: {str(e)}")
        return pd.DataFrame()
