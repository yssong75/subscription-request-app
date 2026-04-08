# -*- coding: utf-8 -*-
"""
본지점 회선 데이터 액세스 (Supabase)
gsheet.py 의 본지점 관련 함수와 동일한 인터페이스 유지
"""
import pandas as pd
import streamlit as st
from datetime import datetime

from db.client import get_supabase


# ── 캐시 TTL (초) ─────────────────────────────────────────────────
_TTL = 300  # 5분


@st.cache_data(ttl=_TTL)
def get_all_branch_data() -> pd.DataFrame:
    """
    branch_lines 전체 조회 (5분 캐싱).
    반환: pandas DataFrame (gsheet.py _get_all_data() 와 동일 구조)
    컬럼 매핑: Supabase → 앱 내부 컬럼명
    """
    try:
        sb = get_supabase()
        res = sb.table("branch_lines").select("*").execute()
        rows = res.data
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        return _rename_to_app_cols(df)
    except Exception as e:
        st.error(f"본지점 데이터 로드 실패: {str(e)}")
        return pd.DataFrame()


def search_branch_data(keyword: str) -> pd.DataFrame:
    """점번/지점명으로 검색 (캐싱된 데이터 사용)"""
    df = get_all_branch_data()
    if df.empty or not keyword or not keyword.strip():
        return df
    kw = keyword.strip()
    mask = (
        df["점번"].astype(str).str.contains(kw, case=False, na=False) |
        df["지점명"].astype(str).str.contains(kw, case=False, na=False)
    )
    return df[mask]


def get_rows_by_점번(점번: str) -> pd.DataFrame:
    """동일 점번의 모든 행 반환 (망분리 탐색용)"""
    df = get_all_branch_data()
    if df.empty:
        return pd.DataFrame()
    return df[df["점번"].astype(str) == str(점번).strip()]


def add_branch_row(data_dict: dict) -> bool:
    """branch_lines 신규 행 추가"""
    try:
        sb = get_supabase()
        row = _app_dict_to_db(data_dict)
        sb.table("branch_lines").insert(row).execute()
        get_all_branch_data.clear()
        get_all_branch_stats.clear()
        return True
    except Exception as e:
        st.error(f"본지점 신규등록 실패: {str(e)}")
        return False


def update_branch_row(점번: str, updates_dict: dict) -> bool:
    """점번 기준으로 branch_lines 업데이트"""
    try:
        sb = get_supabase()
        db_updates = _app_dict_to_db(updates_dict)
        sb.table("branch_lines").update(db_updates).eq("점번", 점번).execute()
        get_all_branch_data.clear()
        get_all_branch_stats.clear()
        return True
    except Exception as e:
        st.error(f"본지점 업데이트 실패: {str(e)}")
        return False


def close_branch_row(점번: str) -> bool:
    """
    폐쇄 처리:
    branch_lines → branch_closures 복사 후 branch_lines 삭제
    """
    try:
        sb = get_supabase()

        # 현재 데이터 조회
        res = sb.table("branch_lines").select("*").eq("점번", 점번).execute()
        if not res.data:
            st.error(f"점번 '{점번}'을 찾을 수 없습니다.")
            return False

        row = res.data[0]

        # branch_closures 에 삽입
        closure = {
            "점번":    row.get("점번"),
            "지점명":  row.get("지점명"),
            "점포구분": row.get("점포구분"),
            "전용회선": row.get("전용회선"),
            "vlan_id":  row.get("vlan_id"),
            "비즈광랜": row.get("비즈광랜"),
            "속도":     row.get("속도"),
            "ap수":     row.get("ap수"),
            "주소":     row.get("주소"),
            "상위국":   row.get("상위국"),
            "폐쇄일":   datetime.now().strftime("%Y-%m-%d"),
        }
        sb.table("branch_closures").insert(closure).execute()

        # branch_lines 에서 삭제
        sb.table("branch_lines").delete().eq("점번", 점번).execute()

        get_all_branch_data.clear()
        get_all_branch_stats.clear()
        get_closure_stats.clear()
        return True

    except Exception as e:
        st.error(f"폐쇄 처리 실패: {str(e)}")
        return False


@st.cache_data(ttl=_TTL)
def get_all_branch_stats() -> dict:
    """본지점 통계 (5분 캐싱)"""
    from config import BRANCH_TYPES
    try:
        df = get_all_branch_data()
        if df.empty:
            return {"total_count": 0, "by_branch_type": {bt: 0 for bt in BRANCH_TYPES}, "all_data": df}
        counts = df["점포구분"].value_counts().to_dict() if "점포구분" in df.columns else {}
        return {
            "total_count": len(df),
            "by_branch_type": {bt: counts.get(bt, 0) for bt in BRANCH_TYPES},
            "all_data": df,
        }
    except Exception as e:
        st.error(f"본지점 통계 실패: {str(e)}")
        from config import BRANCH_TYPES
        return {"total_count": 0, "by_branch_type": {bt: 0 for bt in BRANCH_TYPES}, "all_data": pd.DataFrame()}


@st.cache_data(ttl=_TTL)
def get_closure_stats() -> dict:
    """폐쇄관리 통계 (5분 캐싱)"""
    try:
        sb = get_supabase()
        res = sb.table("branch_closures").select("id", count="exact").execute()
        return {"total_closed": res.count or 0}
    except Exception as e:
        st.error(f"폐쇄 통계 실패: {str(e)}")
        return {"total_closed": 0}


# ── 내부 헬퍼 ───────────────────────────────────────────────────────

def _rename_to_app_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supabase 컬럼명 → 앱 내부 컬럼명 변환
    (gsheet.py 와 동일한 컬럼명으로 맞춤)
    """
    rename_map = {
        "vlan_id": "Vlan ID",
        "ap수":    "AP수",
        "주소":    "주소1",
    }
    return df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


def _app_dict_to_db(d: dict) -> dict:
    """
    앱 내부 dict → Supabase 컬럼명으로 변환
    """
    rename_map = {
        "Vlan ID": "vlan_id",
        "AP수":    "ap수",
        "주소1":   "주소",
        "주소":    "주소",
    }
    result = {}
    skip_cols = {"id", "등록일", "수정일"}  # DB 자동 관리 컬럼
    for k, v in d.items():
        if k in skip_cols:
            continue
        db_key = rename_map.get(k, k)
        result[db_key] = str(v) if v is not None else None
    return result
