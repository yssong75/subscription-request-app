# -*- coding: utf-8 -*-
"""
선불제 / 후불제 데이터 액세스 (Supabase)
gsheet.py 의 섹션별 함수와 동일한 인터페이스 유지

section_key: "선불제" | "후불제"
"""
import pandas as pd
import streamlit as st
from datetime import datetime

from db.client import get_supabase

_TTL = 300

# 섹션별 테이블 매핑
_TABLE_MAP = {
    "선불제": {"data": "prepaid_lines",    "closure": "prepaid_closures"},
    "후불제": {"data": "postpaid_lines",   "closure": "postpaid_closures"},
}

# 앱 컬럼명 ↔ Supabase 컬럼명 매핑 (선불제)
_PREPAID_RENAME = {
    "속도":     "다운속도",
    "약정기간": "계약기간",
}
_PREPAID_RENAME_REVERSE = {v: k for k, v in _PREPAID_RENAME.items()}

# 앱 컬럼명 ↔ Supabase 컬럼명 매핑 (후불제)
_POSTPAID_RENAME = {
    "WIFI수량": "wifi수량",
    "요금":     "비용",
    "LTE번호":  "lte번호",
    "운영상태": "상태",
}
_POSTPAID_RENAME_REVERSE = {v: k for k, v in _POSTPAID_RENAME.items()}


# ══════════════════════════════════════════════════════════════════
# 조회
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=_TTL)
def get_section_data(section_key: str) -> pd.DataFrame:
    """
    섹션별 전체 데이터 조회 (5분 캐싱).
    반환 DataFrame 컬럼은 Google Sheets 원본 컬럼명과 호환.
    """
    try:
        tbl = _TABLE_MAP[section_key]["data"]
        sb = get_supabase()
        res = sb.table(tbl).select("*").execute()
        if not res.data:
            return pd.DataFrame()
        df = pd.DataFrame(res.data)
        return _rename_to_app(df, section_key)
    except Exception as e:
        st.error(f"{section_key} 데이터 조회 실패: {str(e)}")
        return pd.DataFrame()


def search_section_data(section_key: str, keyword: str) -> pd.DataFrame:
    """서비스번호/지점명으로 검색"""
    df = get_section_data(section_key)
    if df.empty or not keyword or not keyword.strip():
        return df
    kw = keyword.strip()
    mask = pd.Series([False] * len(df), index=df.index)
    if "서비스번호" in df.columns:
        mask |= df["서비스번호"].astype(str).str.contains(kw, case=False, na=False)
    if "지점명" in df.columns:
        mask |= df["지점명"].astype(str).str.contains(kw, case=False, na=False)
    return df[mask]


@st.cache_data(ttl=_TTL)
def get_section_closure_data(section_key: str) -> pd.DataFrame:
    """해지 데이터 조회"""
    try:
        tbl = _TABLE_MAP[section_key]["closure"]
        sb = get_supabase()
        res = sb.table(tbl).select("*").order("해지일", desc=True).execute()
        if not res.data:
            return pd.DataFrame()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"{section_key} 해지 데이터 조회 실패: {str(e)}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════
# 쓰기
# ══════════════════════════════════════════════════════════════════

def add_section_row(section_key: str, data_dict: dict) -> bool:
    """섹션별 신규 행 추가"""
    try:
        tbl = _TABLE_MAP[section_key]["data"]
        sb = get_supabase()
        row = _app_dict_to_db(data_dict, section_key)
        sb.table(tbl).insert(row).execute()
        get_section_data.clear()
        return True
    except Exception as e:
        st.error(f"{section_key} 신규등록 실패: {str(e)}")
        return False


def update_section_row(section_key: str, service_no: str, updates: dict) -> bool:
    """서비스번호 기준 업데이트"""
    try:
        tbl = _TABLE_MAP[section_key]["data"]
        sb = get_supabase()
        db_updates = _app_dict_to_db(updates, section_key)
        sb.table(tbl).update(db_updates).eq("서비스번호", service_no).execute()
        get_section_data.clear()
        return True
    except Exception as e:
        st.error(f"{section_key} 업데이트 실패: {str(e)}")
        return False


def close_section_row(section_key: str, service_no: str, close_date: str | None = None) -> bool:
    """
    해지 처리: data 테이블 → closure 테이블 복사 후 삭제
    """
    try:
        if close_date is None:
            close_date = datetime.now().strftime("%Y-%m-%d")

        data_tbl    = _TABLE_MAP[section_key]["data"]
        closure_tbl = _TABLE_MAP[section_key]["closure"]
        sb = get_supabase()

        # 데이터 조회
        res = sb.table(data_tbl).select("*").eq("서비스번호", service_no).execute()
        if not res.data:
            st.error(f"서비스번호 '{service_no}'를 찾을 수 없습니다.")
            return False

        row = res.data[0]

        # closure 테이블 삽입
        closure = _build_closure_row(row, section_key, close_date)
        sb.table(closure_tbl).insert(closure).execute()

        # data 테이블에서 삭제
        sb.table(data_tbl).delete().eq("서비스번호", service_no).execute()

        get_section_data.clear()
        get_section_closure_data.clear()
        return True

    except Exception as e:
        st.error(f"{section_key} 해지 처리 실패: {str(e)}")
        return False


# ══════════════════════════════════════════════════════════════════
# 내부 헬퍼
# ══════════════════════════════════════════════════════════════════

def _rename_to_app(df: pd.DataFrame, section_key: str) -> pd.DataFrame:
    """Supabase 컬럼명 → 앱 내부 컬럼명"""
    if section_key == "선불제":
        return df.rename(columns={k: v for k, v in _PREPAID_RENAME_REVERSE.items() if k in df.columns})
    elif section_key == "후불제":
        return df.rename(columns={k: v for k, v in _POSTPAID_RENAME_REVERSE.items() if k in df.columns})
    return df


def _app_dict_to_db(d: dict, section_key: str) -> dict:
    """앱 dict → Supabase 컬럼명 변환"""
    skip = {"id", "등록일", "수정일"}
    rename = _PREPAID_RENAME if section_key == "선불제" else _POSTPAID_RENAME
    result = {}
    for k, v in d.items():
        if k in skip:
            continue
        db_k = rename.get(k, k)
        result[db_k] = str(v) if (v is not None and str(v).strip()) else None
    return result


def _build_closure_row(row: dict, section_key: str, close_date: str) -> dict:
    """data 행 → closure 행 변환"""
    if section_key == "선불제":
        return {
            "점번":       row.get("점번"),
            "지점명":     row.get("지점명"),
            "서비스번호": row.get("서비스번호"),
            "서비스명":   row.get("서비스명"),
            "요금제":     row.get("요금제"),
            "용도":       row.get("용도"),
            "해지일":     close_date,
            "해지사유":   None,
        }
    else:  # 후불제
        return {
            "구분":       row.get("구분"),
            "점번":       row.get("점번"),
            "지점명":     row.get("지점명"),
            "서비스번호": row.get("서비스번호"),
            "서비스명":   row.get("서비스명"),
            "요금제":     row.get("요금제"),
            "해지일":     close_date,
            "해지사유":   None,
        }
