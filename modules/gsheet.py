# -*- coding: utf-8 -*-
"""
Google Sheets 데이터베이스 처리 모듈
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
from datetime import datetime

from config import SHEET_NAMES, BRANCH_TYPES, SECTIONS


@st.cache_resource
def get_client():
    """
    Google Sheets 클라이언트 생성 (앱 생애주기 동안 1회만 생성)
    secrets.toml 의 [gcp_service_account] 섹션을 사용합니다.
    """
    try:
        if "gcp_service_account" not in st.secrets:
            raise KeyError("secrets.toml 에 [gcp_service_account] 섹션이 없습니다.")
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error("Google Sheets 인증에 실패했습니다. 관리자에게 문의하세요.")
        raise RuntimeError("GSheet 인증 실패") from e


@st.cache_resource
def get_spreadsheet():
    """Spreadsheet 객체 캐싱 (워크시트 접근 공통 진입점)"""
    spreadsheet_id = st.secrets.get("spreadsheet_id", "")
    if not spreadsheet_id:
        st.error("secrets.toml 에 spreadsheet_id 가 설정되지 않았습니다.")
        raise KeyError("spreadsheet_id 누락")
    return get_client().open_by_key(spreadsheet_id)


def get_worksheet(sheet_key):
    """시트명으로 워크시트 반환"""
    return get_spreadsheet().worksheet(SHEET_NAMES[sheet_key])


@st.cache_data(ttl=300)
def _get_all_data():
    """DATA 시트 전체 데이터 캐싱 (5분)"""
    try:
        data = get_worksheet("data").get_all_values()
        if len(data) < 2:
            return pd.DataFrame()
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        st.error(f"데이터 로드 실패: {str(e)}")
        return pd.DataFrame()


def search_data(keyword):
    """
    DATA 시트에서 점번/지점명으로 검색 (캐싱된 데이터 사용)
    """
    try:
        df = _get_all_data()
        if df.empty:
            return df

        if not keyword or keyword.strip() == "":
            return df

        keyword = str(keyword).strip()
        mask = (
            df["점번"].astype(str).str.contains(keyword, case=False, na=False) |
            df["지점명"].astype(str).str.contains(keyword, case=False, na=False)
        )
        return df[mask]

    except Exception as e:
        st.error(f"데이터 검색 실패: {str(e)}")
        return pd.DataFrame()


def get_rows_by_점번(점번):
    """동일 점번의 모든 행 반환 (망분리 탐색용)"""
    try:
        df = _get_all_data()
        if df.empty:
            return pd.DataFrame()
        return df[df["점번"].astype(str) == str(점번).strip()]
    except Exception as e:
        st.error(f"점번 조회 실패: {str(e)}")
        return pd.DataFrame()


def save_request(data_dict):
    """청약요청 시트에 데이터 저장"""
    try:
        worksheet = get_worksheet("request")
        headers = worksheet.row_values(1)
        row_data = [str(data_dict.get(h, "") or "") for h in headers]
        worksheet.append_row(row_data)
        return True
    except Exception as e:
        st.error(f"청약요청 저장 실패: {str(e)}")
        return False


def save_log(data_dict):
    """변경로그 시트에 데이터 저장"""
    try:
        worksheet = get_worksheet("log")
        headers = worksheet.row_values(1)
        row_data = [str(data_dict.get(h, "") or "") for h in headers]
        worksheet.append_row(row_data)
        _get_all_logs.clear()  # 캐시 무효화
        return True
    except Exception as e:
        st.error(f"변경로그 저장 실패: {str(e)}")
        return False


def get_logs(limit=50):
    """
    최근 변경로그 조회 (마지막 행부터 limit개만 처리)
    """
    try:
        ws = get_worksheet("log")
        # 행 수만 먼저 파악해서 필요한 범위만 가져옴
        all_values = ws.get_all_values()
        if len(all_values) < 2:
            return pd.DataFrame()

        headers = all_values[0]
        rows = all_values[1:]
        # 마지막 limit개만 역순으로
        recent_rows = rows[max(0, len(rows) - limit):][::-1]
        return pd.DataFrame(recent_rows, columns=headers)

    except Exception as e:
        st.error(f"변경로그 조회 실패: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_mailing_list():
    """
    메일링 시트에서 이름/이메일 목록 조회 (5분 캐싱)
    """
    try:
        data = get_worksheet("mailing").get_all_values()
        if len(data) < 2:
            return []
        display_list = []
        for row in data[1:]:
            if len(row) >= 2 and row[0].strip() and row[1].strip():
                display_list.append(f"{row[0].strip()}<{row[1].strip()}>")
        return display_list
    except Exception as e:
        st.error(f"메일링 리스트 조회 실패: {str(e)}")
        return []


def update_data_row(점번, updates_dict):
    """
    DATA 시트에서 점번 기준으로 행을 찾아 변경된 컬럼만 업데이트
    """
    try:
        worksheet = get_worksheet("data")

        # 헤더 가져오기
        headers = worksheet.row_values(1)

        # 점번으로 행 찾기
        cell = worksheet.find(str(점번), in_column=headers.index("점번") + 1)
        if cell is None:
            st.error(f"점번 '{점번}'에 해당하는 데이터를 찾을 수 없습니다.")
            return False

        row_num = cell.row

        # 변경된 컬럼만 업데이트
        cells_to_update = []
        for col_name, new_value in updates_dict.items():
            if col_name in headers:
                col_idx = headers.index(col_name) + 1
                cells_to_update.append(
                    gspread.Cell(row_num, col_idx, str(new_value) if new_value is not None else "")
                )

        if cells_to_update:
            worksheet.update_cells(cells_to_update)
            _get_all_data.clear()  # 캐시 무효화

        return True

    except Exception as e:
        st.error(f"DATA 시트 업데이트 실패: {str(e)}")
        return False


def close_branch(점번):
    """
    폐쇄 처리: DATA 시트에서 행 복사 → 폐쇄관리 시트에 추가 → DATA 시트에서 삭제
    """
    try:
        data_ws = get_worksheet("data")
        closure_ws = get_worksheet("closure")

        # DATA 시트 헤더
        data_headers = data_ws.row_values(1)

        # 점번으로 행 찾기
        cell = data_ws.find(str(점번), in_column=data_headers.index("점번") + 1)
        if cell is None:
            st.error(f"점번 '{점번}'에 해당하는 데이터를 찾을 수 없습니다.")
            return False

        row_num = cell.row
        row_data = data_ws.row_values(row_num)

        # 폐쇄관리 시트 헤더 확인
        closure_headers = closure_ws.row_values(1)

        # DATA 행 데이터를 dict로 변환
        data_dict = {}
        for i, header in enumerate(data_headers):
            data_dict[header] = row_data[i] if i < len(row_data) else ""

        # 사용여부를 "폐쇄"로 설정
        data_dict["사용여부"] = f"폐쇄({datetime.now().strftime('%Y-%m-%d')})"

        # 폐쇄관리 시트에 추가 (헤더 순서대로)
        closure_row = []
        for header in closure_headers:
            closure_row.append(str(data_dict.get(header, "") or ""))
        closure_ws.append_row(closure_row)

        # DATA 시트에서 해당 행 삭제
        data_ws.delete_rows(row_num)

        # 캐시 무효화 (폐쇄 후 즉시 반영)
        _get_all_data.clear()
        get_all_data_stats.clear()
        get_closure_stats.clear()

        return True

    except Exception as e:
        st.error(f"폐쇄 처리 실패: {str(e)}")
        return False


def generate_change_summary(original, updated):
    """
    원본과 수정 데이터를 비교하여 변경 요약 태그 생성

    Args:
        original (dict): 원본 데이터 (DATA 시트 기준 컬럼명)
        updated (dict): 수정된 데이터 (DATA 시트 기준 컬럼명)

    Returns:
        str: 변경 요약 태그 (예: "#주소지 변경, #와이파이 수량 변경")
    """
    field_tag_map = {
        "지점명": "#영업점명 변경",
        "점포구분": "#점포구분 변경",
        "전용회선": "#서비스번호 변경",
        "Vlan ID": "#Vlan ID 변경",
        "비즈광랜": "#비즈광랜 변경",
        "속도": "#속도 변경",
        "AP수": "#와이파이 수량 변경",
        "상위국": "#상위국 변경",
        "주소1": "#주소지 변경",
    }

    tags = []
    for field, tag in field_tag_map.items():
        old_val = str(original.get(field, "")).strip()
        new_val = str(updated.get(field, "")).strip()
        if old_val != new_val:
            tags.append(tag)

    return ", ".join(tags) if tags else ""


def generate_request_id():
    """
    청약 요청 ID 생성 (현재 시각 기반)

    Returns:
        str: 요청 ID (예: REQ20240123143055)
    """
    now = datetime.now()
    request_id = f"REQ{now.strftime('%Y%m%d%H%M%S')}"
    return request_id


def add_data_row(data_dict):
    """DATA 시트에 신규 행 추가"""
    try:
        worksheet = get_worksheet("data")
        headers = worksheet.row_values(1)
        row_data = [str(data_dict.get(h, "") or "") for h in headers]
        worksheet.append_row(row_data)
        _get_all_data.clear()  # 캐시 무효화
        return True
    except Exception as e:
        st.error(f"DATA 시트 신규 등록 실패: {str(e)}")
        return False


@st.cache_data(ttl=300)
def get_all_data_stats():
    """DATA 시트 전체 통계 조회 (5분 캐싱, 캐싱된 데이터 재활용)"""
    try:
        df = _get_all_data()
        if df.empty:
            by_branch = {bt: 0 for bt in BRANCH_TYPES}
            return {"total_count": 0, "by_branch_type": by_branch, "all_data": df}

        total_count = len(df)
        counts = df["점포구분"].value_counts().to_dict() if "점포구분" in df.columns else {}
        by_branch = {bt: counts.get(bt, 0) for bt in BRANCH_TYPES}

        return {"total_count": total_count, "by_branch_type": by_branch, "all_data": df}

    except Exception as e:
        st.error(f"DATA 통계 조회 실패: {str(e)}")
        return {"total_count": 0, "by_branch_type": {bt: 0 for bt in BRANCH_TYPES}, "all_data": pd.DataFrame()}


@st.cache_data(ttl=300)
def _get_all_logs():
    """변경로그 전체 캐싱 (5분)"""
    try:
        data = get_worksheet("log").get_all_values()
        if len(data) < 2:
            return pd.DataFrame()
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def get_monthly_changes(year, month):
    """월별 변경로그 조회 (캐싱된 로그 재활용)"""
    try:
        df = _get_all_logs()
        if df.empty:
            return {"total_changes": 0, "by_work_type": {}, "changes_list": pd.DataFrame()}

        df["_parsed_dt"] = pd.to_datetime(df["변경시각"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
        mask = (df["_parsed_dt"].dt.year == year) & (df["_parsed_dt"].dt.month == month)
        filtered = df[mask].drop(columns=["_parsed_dt"])

        by_work = filtered["작업구분"].value_counts().to_dict() if "작업구분" in filtered.columns else {}
        return {"total_changes": len(filtered), "by_work_type": by_work, "changes_list": filtered}

    except Exception as e:
        st.error(f"월별 변경로그 조회 실패: {str(e)}")
        return {"total_changes": 0, "by_work_type": {}, "changes_list": pd.DataFrame()}


@st.cache_data(ttl=300)
def get_closure_stats():
    """폐쇄관리 시트 통계 조회 (5분 캐싱)"""
    try:
        data = get_worksheet("closure").get_all_values()
        return {"total_closed": max(0, len(data) - 1)}
    except Exception as e:
        st.error(f"폐쇄관리 통계 조회 실패: {str(e)}")
        return {"total_closed": 0}


@st.cache_data(ttl=600)
def _get_all_users():
    """사용자 시트 전체 캐싱 (10분)"""
    try:
        data = get_worksheet("users").get_all_values()
        if len(data) < 2:
            return []
        headers = data[0]
        return [dict(zip(headers, row)) for row in data[1:]]
    except Exception:
        return []


def get_user(user_id):
    """사용자 시트에서 아이디로 사용자 조회 (캐싱된 데이터 사용)"""
    try:
        users = _get_all_users()
        for u in users:
            if u.get("아이디", "").strip() == user_id.strip():
                return u
        return None
    except Exception:
        return None


def register_user(user_data):
    """사용자 시트에 신규 사용자 등록"""
    try:
        worksheet = get_worksheet("users")
        headers = worksheet.row_values(1)
        row_data = [str(user_data.get(h, "") or "") for h in headers]
        worksheet.append_row(row_data)
        _get_all_users.clear()  # 캐시 무효화
        return True
    except Exception:
        return False


def update_user(user_id, updates_dict):
    """사용자 시트에서 아이디 기준으로 사용자 정보 업데이트"""
    try:
        worksheet = get_worksheet("users")

        headers = worksheet.row_values(1)

        # 아이디로 행 찾기
        id_col = headers.index("아이디") + 1
        cell = worksheet.find(str(user_id), in_column=id_col)
        if cell is None:
            return False

        row_num = cell.row

        # 변경된 컬럼만 업데이트
        cells_to_update = []
        for col_name, new_value in updates_dict.items():
            if col_name in headers:
                col_idx = headers.index(col_name) + 1
                cells_to_update.append(
                    gspread.Cell(row_num, col_idx, str(new_value) if new_value is not None else "")
                )

        if cells_to_update:
            worksheet.update_cells(cells_to_update)
            _get_all_users.clear()

        return True

    except Exception as e:
        return False


# ===================================================================
# 선불제 / 후불제 공통 CRUD
# ===================================================================

@st.cache_data(ttl=300)
def get_section_data(section_key):
    """섹션별(선불제/후불제) DATA 시트 전체 조회 (5분 캐싱)"""
    try:
        section = SECTIONS[section_key]
        data = get_worksheet(section["data_sheet"]).get_all_values()
        if len(data) < 2:
            return pd.DataFrame()
        return pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        st.error(f"{section_key} 데이터 조회 실패: {str(e)}")
        return pd.DataFrame()


def search_section_data(section_key, keyword):
    """섹션별 데이터 검색 (캐싱된 데이터 사용)"""
    try:
        df = get_section_data(section_key)
        if df.empty:
            return df
        keyword = str(keyword).strip()
        mask = pd.Series([False] * len(df))
        if "서비스번호" in df.columns:
            mask |= df["서비스번호"].astype(str).str.contains(keyword, case=False, na=False)
        if "지점명" in df.columns:
            mask |= df["지점명"].astype(str).str.contains(keyword, case=False, na=False)
        return df[mask]
    except Exception as e:
        st.error(f"검색 실패: {str(e)}")
        return pd.DataFrame()


def add_section_row(section_key, data_dict):
    """섹션별 DATA 시트에 신규 행 추가"""
    try:
        section = SECTIONS[section_key]
        worksheet = get_worksheet(section["data_sheet"])
        headers = worksheet.row_values(1)
        row_data = [str(data_dict.get(h, "") or "") for h in headers]
        worksheet.append_row(row_data)
        get_section_data.clear()  # 캐시 무효화
        return True
    except Exception as e:
        st.error(f"{section_key} 신규등록 실패: {str(e)}")
        return False


def close_section_row(section_key, service_no, close_date=None):
    """섹션별 DATA -> 해지 시트로 이동"""
    try:
        if close_date is None:
            close_date = datetime.now().strftime('%Y-%m-%d')

        section = SECTIONS[section_key]
        data_ws = get_worksheet(section["data_sheet"])
        closure_ws = get_worksheet(section["closure_sheet"])

        data_all = data_ws.get_all_values()
        headers = data_all[0]
        closure_headers = closure_ws.row_values(1)

        svc_col_idx = headers.index("서비스번호")
        target_row = None
        target_row_idx = None
        for idx, row in enumerate(data_all[1:], 2):
            if str(row[svc_col_idx]).strip() == str(service_no).strip():
                target_row = row
                target_row_idx = idx
                break

        if target_row is None:
            st.error(f"서비스번호 {service_no}를 찾을 수 없습니다.")
            return False

        row_dict = dict(zip(headers, target_row))
        closure_row = []
        for ch in closure_headers:
            if ch == "해지일":
                closure_row.append(close_date)
            else:
                closure_row.append(row_dict.get(ch, ""))
        closure_ws.append_row(closure_row)

        data_ws.delete_rows(target_row_idx)
        get_section_data.clear()  # 캐시 무효화
        return True

    except Exception as e:
        st.error(f"{section_key} 해지 처리 실패: {str(e)}")
        return False


@st.cache_data(ttl=300)
def get_section_stats(section_key):
    """섹션별 통계 조회 (캐싱된 데이터 재활용)"""
    try:
        df = get_section_data(section_key)
        section = SECTIONS[section_key]
        closure_data = get_worksheet(section["closure_sheet"]).get_all_values()
        return {"total": len(df), "closed": max(0, len(closure_data) - 1)}
    except Exception:
        return {"total": 0, "closed": 0}


def save_unified_log(section_key, log_data):
    """통합 변경로그에 기록 (분류 컬럼 포함)"""
    try:
        log_ws = get_worksheet("log")
        headers = log_ws.row_values(1)

        if "분류" not in headers:
            headers.append("분류")
            log_ws.update_cell(1, len(headers), "분류")

        log_data["분류"] = section_key
        if "변경시각" not in log_data:
            log_data["변경시각"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        row = []
        for h in headers:
            value = log_data.get(h, "")
            row.append(str(value) if value is not None else "")
        log_ws.append_row(row)
        _get_all_logs.clear()
        get_monthly_changes.clear()
        return True
    except Exception as e:
        st.error(f"변경로그 기록 실패: {str(e)}")
        return False
