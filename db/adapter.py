# -*- coding: utf-8 -*-
"""
gsheet.py → db/ 모듈 전환 어댑터
====================================
app.py 의 import 한 줄만 바꾸면 Google Sheets ↔ Supabase 전환 가능.

사용법:
    # 기존 (Google Sheets)
    from modules.gsheet import search_data, add_data_row, ...

    # 신규 (Supabase)
    from db.adapter import search_data, add_data_row, ...

모든 함수는 gsheet.py 와 동일한 시그니처/반환타입을 유지합니다.
"""

# ── 본지점 ────────────────────────────────────────────────────────
from db.branch import (
    get_all_branch_data        as _get_all_data,
    search_branch_data         as search_data,
    get_rows_by_점번,
    add_branch_row             as add_data_row,
    update_branch_row          as _update_branch_row,
    close_branch_row           as close_branch,
    get_all_branch_stats       as get_all_data_stats,
    get_closure_stats,
)

# ── 섹션별 (선불제/후불제) ──────────────────────────────────────────
from db.sections import (
    get_section_data,
    search_section_data,
    add_section_row,
    update_section_row,
    close_section_row,
    get_section_closure_data,
)

# ── 공통 ──────────────────────────────────────────────────────────
from db.common import (
    get_user,
    register_user,
    update_user,
    get_mailing_list,
    save_request,
    get_requests,
    generate_request_id,
    save_log,
    get_logs,
    get_monthly_changes,
)


# ── gsheet.py 와 시그니처가 다른 함수들의 래퍼 ────────────────────

def update_data_row(점번: str, updates_dict: dict) -> bool:
    """
    gsheet.py update_data_row 호환 래퍼.
    점번 기준으로 branch_lines 업데이트.
    """
    return _update_branch_row(점번, updates_dict)


def save_unified_log(section_key: str, log_data: dict) -> bool:
    """
    gsheet.py save_unified_log 호환 래퍼.
    section_key('본지점'|'선불제'|'후불제')를 log_data['분류']에 삽입하여 저장.
    """
    merged = dict(log_data)
    merged.setdefault("분류", section_key)
    return save_log(merged)


def get_all_data_cached():
    """_get_all_data() 의 공개 래퍼"""
    return _get_all_data()


# ── 통계 래퍼 ─────────────────────────────────────────────────────

def get_closure_count() -> int:
    """폐쇄 건수 반환"""
    return get_closure_stats().get("total_closed", 0)


def get_section_stats(section_key: str) -> dict:
    """섹션별 통계 조회 (active + closed)"""
    df_active = get_section_data(section_key)
    df_closed = get_section_closure_data(section_key)
    return {
        "total":  len(df_active),
        "closed": len(df_closed),
    }


# ── 순수 Python 유틸 ──────────────────────────────────────────────

def generate_change_summary(original: dict, updated: dict) -> str:
    """
    원본/수정 데이터를 비교하여 변경 요약 태그 문자열 반환.
    gsheet.py 와 동일한 로직 (DB 없는 순수 함수).
    """
    field_tag_map = {
        "지점명":   "#영업점명 변경",
        "점포구분": "#점포구분 변경",
        "전용회선": "#서비스번호 변경",
        "Vlan ID":  "#Vlan ID 변경",
        "비즈광랜": "#비즈광랜 변경",
        "속도":     "#속도 변경",
        "AP수":     "#와이파이 수량 변경",
        "상위국":   "#상위국 변경",
        "주소1":    "#주소지 변경",
    }
    tags = []
    for field, tag in field_tag_map.items():
        if str(original.get(field, "")).strip() != str(updated.get(field, "")).strip():
            tags.append(tag)
    return ", ".join(tags) if tags else ""
