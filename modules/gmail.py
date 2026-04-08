# -*- coding: utf-8 -*-
"""
Gmail SMTP를 통한 이메일 발송 모듈
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

from config import REPORT_COLORS, BRANCH_TYPES, SECTIONS


def _build_email_signature():
    """secrets.toml [signature] 섹션에서 메일 서명 HTML 생성"""
    sig = st.secrets.get("signature", {})
    name     = sig.get("name", "")
    title    = sig.get("title", "")
    company  = sig.get("company", "")
    dept     = sig.get("dept", "")
    email    = sig.get("email", "")
    phone    = sig.get("phone", "")
    address  = sig.get("address", "")
    address2 = sig.get("address2", "")

    if not name:
        return ""

    addr_html = ""
    if address:
        addr_html = f"{address}"
        if address2:
            addr_html += f"<br>{address2}"

    return f"""
<div style="margin-top: 20px;">
    <p style="margin: 8px 0; line-height: 1.6;">이상입니다.</p>
    <p style="margin: 8px 0 20px 0; line-height: 1.6;">감사합니다.</p>
    <div style="height: 2px; background: #3A7D7D; margin: 20px 0;"></div>
    <table cellpadding="0" cellspacing="0" border="0" style="max-width:600px;margin:20px 0;background:#ffffff;border-radius:11px;box-shadow:0 2px 14px rgba(0,0,0,0.06);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;">
        <tr>
            <td style="padding:22px 28px;vertical-align:middle;width:40%;">
                <div style="font-size:18px;font-weight:700;color:#1d1d1f;letter-spacing:-0.3px;margin-bottom:3px;">{name}</div>
                <div style="font-size:11px;color:#86868b;font-weight:400;margin-bottom:14px;">{title}</div>
                <div style="font-size:12px;color:#1d1d1f;font-weight:600;letter-spacing:-0.1px;">{company}</div>
                <div style="font-size:10px;color:#6e6e73;margin-top:2px;">{dept}</div>
            </td>
            <td style="width:1px;padding:16px 0;vertical-align:middle;">
                <div style="width:1px;height:80px;background:#d2d2d7;"></div>
            </td>
            <td style="padding:22px 28px;vertical-align:middle;">
                <table cellpadding="0" cellspacing="0" border="0" style="width:100%;">
                    {"" if not email else f'<tr><td style="padding:5px 0;font-size:11px;color:#1d1d1f;"><span style="color:#0071e3;font-size:13px;vertical-align:middle;margin-right:8px;">&#9993;</span><a href="mailto:{email}" style="color:#0071e3;text-decoration:none;">{email}</a></td></tr>'}
                    {"" if not phone else f'<tr><td style="padding:5px 0;font-size:11px;color:#1d1d1f;"><span style="color:#0071e3;font-size:13px;vertical-align:middle;margin-right:8px;">&#9742;</span><a href="tel:{phone}" style="color:#0071e3;text-decoration:none;">{phone}</a></td></tr>'}
                    {"" if not addr_html else f'<tr><td style="padding:8px 0 0 0;font-size:10px;color:#86868b;line-height:1.5;border-top:1px solid #f5f5f7;">{addr_html}</td></tr>'}
                </table>
            </td>
        </tr>
    </table>
</div>
"""


def _get_work_type_badge(work_type):
    """작업구분에 따른 배지 스타일 반환"""
    badge_styles = {
        "주소지이전": ("background:#E8F4F4;color:#3A7D7D;", "주소지이전"),
        "층간이전":  ("background:#E8F4F4;color:#3A7D7D;", "층간이전"),
        "층내이전":  ("background:#E8F4F4;color:#3A7D7D;", "층내이전"),
        "폐쇄":     ("background:#FDECEC;color:#9D5B5B;", "폐쇄"),
        "신규":     ("background:#ECF4EC;color:#5D7E5D;", "신규"),
        "감속":     ("background:#FFF3E0;color:#E65100;", "감속"),
        "증속":     ("background:#E3F2FD;color:#1565C0;", "증속"),
    }
    style, label = badge_styles.get(work_type, ("background:#FFF8EC;color:#8B7355;", work_type))
    return f'<span style="display:inline-block;padding:4px 14px;border-radius:20px;font-size:13px;font-weight:600;{style}">{label}</span>'


def create_email_html(data):
    """
    청약 요청서 HTML 템플릿 생성

    Args:
        data (dict): 청약 데이터

    Returns:
        str: HTML 본문
    """
    from datetime import datetime

    인사말 = data.get('메일인사말', '').replace('\n', '<br>')
    사용자서명 = data.get('메일서명', '').replace('\n', '<br>')
    _기본서명 = _build_email_signature()

    if 사용자서명:
        서명 = f"<p style='margin:8px 0;line-height:1.6;'>{사용자서명}</p>{_기본서명}"
    else:
        서명 = _기본서명

    접수일 = datetime.now().strftime('%Y-%m-%d')
    작업구분_배지 = _get_work_type_badge(data.get('작업구분', ''))

    # 공통 스타일
    label_style = "padding:10px 14px;color:#5B6B7D;font-size:13px;font-weight:400;width:25%;vertical-align:middle;border:none;border-bottom:1px solid #F5F5F5;"
    value_style = "padding:10px 14px;color:#2C2C2C;font-size:14px;font-weight:500;width:25%;vertical-align:middle;border:none;border-bottom:1px solid #F5F5F5;"
    table_style = "border-collapse:collapse;width:100%;border:none;"

    # 전용회선 / 망분리 / 비즈광랜 조건부 행 (값이 있을 때만 이메일에 포함)
    _전용회선 = data.get('전용회선', '')
    _망분리_전용회선 = data.get('망분리_전용회선', '')
    _망분리_속도 = data.get('망분리_속도', '')
    _비즈광랜 = data.get('비즈광랜', '')

    # 본부부서는 Vlan ID 미사용 → 속도 표시, 그 외 Vlan ID 표시
    _is_본부부서 = data.get('점포구분', '') == '본부부서'
    _전용회선_2nd_label = '속도' if _is_본부부서 else 'Vlan ID'
    _전용회선_2nd_value = data.get('속도', '') if _is_본부부서 else data.get('Vlan ID', '')

    _전용회선_row = f"""<tr>
                        <td style="{label_style}">전용회선</td>
                        <td style="{value_style}">{_전용회선}</td>
                        <td style="{label_style}">{_전용회선_2nd_label}</td>
                        <td style="{value_style}">{_전용회선_2nd_value}</td>
                    </tr>""" if _전용회선 else ""

    _망분리_row = f"""<tr>
                        <td style="{label_style}">망분리</td>
                        <td style="{value_style}">{_망분리_전용회선}</td>
                        <td style="{label_style}">망분리 속도</td>
                        <td style="{value_style}">{_망분리_속도}</td>
                    </tr>""" if _망분리_전용회선 else ""

    _비즈광랜_row = f"""<tr>
                        <td style="{label_style}">비즈광랜</td>
                        <td style="{value_style}">{_비즈광랜}</td>
                        <td style="{label_style}">속도</td>
                        <td style="{value_style}">{data.get('속도', '')}</td>
                    </tr>""" if _비즈광랜 else ""

    html_body = f"""
    <div style="width:100%;background:#F5F5F5;padding:20px 0;margin:0;font-family:'Malgun Gothic','Apple SD Gothic Neo','Segoe UI',sans-serif;">
      <div style="max-width:800px;margin:0 auto;padding:0 20px;">

        <!-- 인사말 -->
        <div style="padding:0 0 16px 0;line-height:1.8;color:#2C2C2C;font-size:14px;">
            {인사말}
        </div>

        <!-- 헤더 -->
        <div style="background:linear-gradient(135deg,#3A7D7D,#2D6363);border-radius:12px 12px 0 0;padding:28px 32px;">
            <h2 style="margin:0;color:#FFFFFF;font-size:20px;font-weight:700;letter-spacing:-0.3px;">청약 요청서</h2>
            <p style="margin:6px 0 0 0;color:rgba(255,255,255,0.75);font-size:13px;">접수일: {접수일}</p>
        </div>

        <!-- 핵심 정보 하이라이트 카드 -->
        <div style="background:#E8F4F4;padding:20px 32px;border-bottom:1px solid #D0E8E8;">
            <table style="border-collapse:collapse;width:100%;border:none;">
                <tr>
                    <td style="padding:4px 0;border:none;width:33%;">
                        <div style="color:#5B6B7D;font-size:11px;margin-bottom:4px;">지점명</div>
                        <div style="color:#2C2C2C;font-size:18px;font-weight:700;">{data.get('지점명', '')}</div>
                    </td>
                    <td style="padding:4px 0;border:none;width:33%;text-align:center;">
                        <div style="color:#5B6B7D;font-size:11px;margin-bottom:4px;">작업구분</div>
                        <div>{작업구분_배지}</div>
                    </td>
                    <td style="padding:4px 0;border:none;width:33%;text-align:right;">
                        <div style="color:#5B6B7D;font-size:11px;margin-bottom:4px;">작업요청일</div>
                        <div style="color:#2C2C2C;font-size:18px;font-weight:700;">{data.get('요청일', '')}</div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- 콘텐츠 영역 -->
        <div style="background:#FAFAFA;padding:24px 32px 32px 32px;border-radius:0 0 12px 12px;">

            <!-- 기본 서비스 정보 -->
            <div style="background:#FFFFFF;border:1px solid #E8E8E8;border-radius:10px;margin-bottom:20px;overflow:hidden;">
                <div style="padding:14px 18px;border-bottom:1px solid #F0F0F0;">
                    <div style="display:inline-block;width:4px;height:16px;background:#3A7D7D;border-radius:2px;vertical-align:middle;margin-right:10px;">&#8203;</div>
                    <span style="font-size:15px;font-weight:700;color:#2C2C2C;vertical-align:middle;">기본 서비스 정보</span>
                </div>
                <table style="{table_style}">
                    <tr>
                        <td style="{label_style}">점번</td>
                        <td style="{value_style}">{data.get('점번', '')}</td>
                        <td style="{label_style}">지점명</td>
                        <td style="{value_style}">{data.get('지점명', '')}</td>
                    </tr>
                    {_전용회선_row}
                    {_망분리_row}
                    {_비즈광랜_row}
                    <tr>
                        <td style="{label_style}">와이파이 수량</td>
                        <td style="{value_style}">{data.get('AP수', '')}</td>
                        <td style="{label_style}">&nbsp;</td>
                        <td style="{value_style}">&nbsp;</td>
                    </tr>
                </table>
            </div>

            <!-- 주소지 정보 -->
            <div style="background:#FFFFFF;border:1px solid #E8E8E8;border-radius:10px;margin-bottom:20px;overflow:hidden;">
                <div style="padding:14px 18px;border-bottom:1px solid #F0F0F0;">
                    <div style="display:inline-block;width:4px;height:16px;background:#5D7E5D;border-radius:2px;vertical-align:middle;margin-right:10px;">&#8203;</div>
                    <span style="font-size:15px;font-weight:700;color:#2C2C2C;vertical-align:middle;">주소지 정보</span>
                </div>
                <table style="{table_style}">
                    <tr>
                        <td style="{label_style}width:20%;">상위국</td>
                        <td style="{value_style}width:80%;">{data.get('상위국', '')}</td>
                    </tr>
                    <tr>
                        <td style="{label_style}width:20%;">변경 전</td>
                        <td style="padding:10px 14px;font-size:14px;font-weight:500;border:none;border-bottom:1px solid #F5F5F5;background:#FFF5F5;color:#9D5B5B;">{data.get('변경전주소', '')}</td>
                    </tr>
                    <tr>
                        <td style="{label_style}width:20%;">변경 후</td>
                        <td style="padding:10px 14px;font-size:14px;font-weight:500;border:none;border-bottom:1px solid #F5F5F5;background:#F0FFF0;color:#3D7A3D;">{data.get('변경후주소', '')}</td>
                    </tr>
                </table>
            </div>

            <!-- 작업 요청 사항 -->
            <div style="background:#FFFFFF;border:1px solid #E8E8E8;border-radius:10px;margin-bottom:20px;overflow:hidden;">
                <div style="padding:14px 18px;border-bottom:1px solid #F0F0F0;">
                    <div style="display:inline-block;width:4px;height:16px;background:#9D5B5B;border-radius:2px;vertical-align:middle;margin-right:10px;">&#8203;</div>
                    <span style="font-size:15px;font-weight:700;color:#2C2C2C;vertical-align:middle;">작업 요청 사항</span>
                </div>
                <table style="{table_style}">
                    <tr>
                        <td style="{label_style}">작업구분</td>
                        <td style="{value_style}">{작업구분_배지}</td>
                        <td style="{label_style}">이동거리/층</td>
                        <td style="{value_style}">{data.get('거리층', '')}</td>
                    </tr>
                    <tr>
                        <td style="{label_style}">작업요청일</td>
                        <td style="{value_style}">{data.get('요청일', '')}</td>
                        <td style="{label_style}">작업시간</td>
                        <td style="{value_style}">{data.get('작업시간', '')}</td>
                    </tr>
                    <tr>
                        <td style="{label_style}">현장담당자</td>
                        <td style="{value_style}">{data.get('담당자', '')}</td>
                        <td style="{label_style}">전화번호</td>
                        <td style="{value_style}">{data.get('전화번호', '')}</td>
                    </tr>
                    <tr>
                        <td style="{label_style}">요청사항</td>
                        <td colspan="3" style="{value_style}; white-space: pre-line;">{data.get('요청사항', '').replace(chr(10), '<br>')}</td>
                    </tr>
                </table>
            </div>

        </div>

        <!-- 서명 -->
        <div style="margin-top:24px;">
            {서명}
        </div>

        <!-- 푸터 -->
        <p style="color:#AAAAAA;font-size:11px;margin-top:24px;text-align:center;">
            본 청약 요청은 KB 청약요청 시스템을 통해 자동 생성되었습니다.
        </p>

      </div>
    </div>
    """

    return html_body


def _build_message(from_addr, to_emails, subject, body_html, cc_emails=None):
    """MIME 메시지 공통 생성"""
    message = MIMEMultipart('alternative')
    message['From'] = from_addr
    message['To'] = ', '.join(to_emails)
    message['Subject'] = subject
    if cc_emails:
        message['Cc'] = ', '.join(cc_emails)
    message.attach(MIMEText(body_html, 'html', 'utf-8'))
    return message


def send_email(to_emails, subject, body_html, cc_emails=None, bcc_emails=None):
    """
    이메일 발송 - 회사 SMTP 우선, 미설정 시 Gmail 폴백
    """
    recipients = to_emails.copy()
    if cc_emails:
        recipients.extend(cc_emails)
    if bcc_emails:
        recipients.extend(bcc_emails)

    # ── 회사 SMTP 시도 ──────────────────────────────
    smtp_server   = st.secrets.get("smtp_server", "")
    smtp_port     = int(st.secrets.get("smtp_port", 25))
    smtp_user     = st.secrets.get("smtp_user", "")
    smtp_password = st.secrets.get("smtp_password", "")
    smtp_from     = st.secrets.get("smtp_from", "") or smtp_user

    if smtp_server and smtp_user and smtp_password:
        try:
            message = _build_message(smtp_from, to_emails, subject, body_html, cc_emails)

            if smtp_port == 465:
                # SSL 직접 연결
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                    server.login(smtp_user, smtp_password)
                    server.send_message(message, to_addrs=recipients)
            else:
                # 25 또는 587 → STARTTLS 시도
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.ehlo()
                    try:
                        server.starttls()
                        server.ehlo()
                    except smtplib.SMTPException:
                        pass  # STARTTLS 미지원 서버면 평문으로 진행
                    server.login(smtp_user, smtp_password)
                    server.send_message(message, to_addrs=recipients)

            return True

        except Exception:
            st.warning("회사 메일 서버 발송 실패. Gmail로 재시도합니다...")

    # ── Gmail 폴백 ──────────────────────────────────
    gmail_user     = st.secrets.get("gmail_user_email")
    gmail_password = st.secrets.get("gmail_app_password")

    if not gmail_user or not gmail_password:
        st.error("메일 인증 정보가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인하세요.")
        return False

    try:
        message = _build_message(gmail_user, to_emails, subject, body_html, cc_emails)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(message, to_addrs=recipients)
        return True

    except Exception as e:
        st.error(f"이메일 발송 실패: {str(e)}")
        return False


def create_report_html(stats_data, changes_data, closure_data, period_str, section_stats=None):
    """
    월별 레포트 HTML 이메일 템플릿 생성

    Args:
        stats_data (dict): get_all_data_stats() 결과
        changes_data (dict): get_monthly_changes() 결과
        closure_data (dict): get_closure_stats() 결과
        period_str (str): 레포트 기간 (예: "2025년 1월")
        section_stats (dict, optional): 섹션별 통계 {"본지점": {"total": N, "closed": N}, ...}

    Returns:
        str: HTML 본문
    """
    from datetime import datetime

    total_count = stats_data["total_count"]
    by_branch = stats_data["by_branch_type"]
    total_changes = changes_data["total_changes"]
    by_work = changes_data["by_work_type"]
    total_closed = closure_data["total_closed"]
    changes_list = changes_data["changes_list"]

    # 전체 합산 (섹션 통계가 있으면)
    if section_stats:
        grand_total = sum(s.get("total", 0) for s in section_stats.values())
        grand_closed = sum(s.get("closed", 0) for s in section_stats.values())
    else:
        grand_total = total_count
        grand_closed = total_closed

    생성일 = datetime.now().strftime('%Y-%m-%d')

    # 색상
    c = REPORT_COLORS
    bar_colors = c["bar_colors"]
    card_total_bg, card_total_accent = c["card_total"]
    card_active_bg, card_active_accent = c["card_active"]
    card_closed_bg, card_closed_accent = c["card_closed"]
    card_changes_bg, card_changes_accent = c["card_changes"]

    font_family = "'Malgun Gothic','Apple SD Gothic Neo','Segoe UI',sans-serif"

    # ===== 섹션 1: 헤더 =====
    header_html = f"""
    <div style="background-color:{c['primary_start']};background:linear-gradient(135deg,{c['primary_start']},{c['primary_end']});border-radius:10px 10px 0 0;padding:32px 28px;">
        <h2 style="margin:0;color:#FFFFFF;font-size:22px;font-weight:700;letter-spacing:-0.3px;">KB 회선관리 월별 레포트</h2>
        <p style="margin:8px 0 0 0;color:rgba(255,255,255,0.8);font-size:14px;">{period_str}</p>
        <p style="margin:4px 0 0 0;color:rgba(255,255,255,0.6);font-size:12px;">생성일: {생성일}</p>
    </div>
    <div style="height:4px;background:linear-gradient(90deg,#3282B8,#0F9B8E,#F28B30,#8B5CF6);margin-bottom:10px;"></div>
    """

    # ===== 섹션 2: 요약 카드 4개 =====
    cards_html = f"""
    <div style="background:#F8FAFC;padding:20px 12px;border:1px solid #E2E8F0;border-radius:10px;margin-bottom:10px;">
        <table cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;border-spacing:12px 0;">
            <tr>
                <td style="width:25%;vertical-align:top;">
                    <div style="padding:20px 8px;text-align:center;border-radius:10px;background:{card_total_bg};">
                        <div style="color:#64748B;font-size:12px;margin-bottom:8px;">전체 회선수</div>
                        <div style="color:{card_total_accent};font-size:32px;font-weight:800;line-height:1;">{grand_total:,}</div>
                        <div style="color:#94A3B8;font-size:11px;margin-top:6px;">개 회선</div>
                    </div>
                </td>
                <td style="width:25%;vertical-align:top;">
                    <div style="padding:20px 8px;text-align:center;border-radius:10px;background:{card_active_bg};">
                        <div style="color:#64748B;font-size:12px;margin-bottom:8px;">운용 회선</div>
                        <div style="color:{card_active_accent};font-size:32px;font-weight:800;line-height:1;">{grand_total - grand_closed:,}</div>
                        <div style="color:#94A3B8;font-size:11px;margin-top:6px;">개 운용</div>
                    </div>
                </td>
                <td style="width:25%;vertical-align:top;">
                    <div style="padding:20px 8px;text-align:center;border-radius:10px;background:{card_closed_bg};">
                        <div style="color:#64748B;font-size:12px;margin-bottom:8px;">폐쇄/해지</div>
                        <div style="color:{card_closed_accent};font-size:32px;font-weight:800;line-height:1;">{grand_closed:,}</div>
                        <div style="color:#94A3B8;font-size:11px;margin-top:6px;">개 종료</div>
                    </div>
                </td>
                <td style="width:25%;vertical-align:top;">
                    <div style="padding:20px 8px;text-align:center;border-radius:10px;background:{card_changes_bg};">
                        <div style="color:#64748B;font-size:12px;margin-bottom:8px;">월간 변동</div>
                        <div style="color:{card_changes_accent};font-size:32px;font-weight:800;line-height:1;">{total_changes:,}</div>
                        <div style="color:#94A3B8;font-size:11px;margin-top:6px;">건 변동</div>
                    </div>
                </td>
            </tr>
        </table>
    </div>
    """

    # ===== 섹션 2.5: 섹션별 현황 카드 (본지점/선불제/후불제) =====
    section_cards_html = ""
    if section_stats:
        section_colors = c.get("section_colors", {})
        section_cells = ""
        for sec_key, sec_info in SECTIONS.items():
            sec_stat = section_stats.get(sec_key, {"total": 0, "closed": 0})
            sec_bg, sec_accent = section_colors.get(sec_key, ("#F0F0F0", "#333333"))
            sec_icon = sec_info.get("icon", "")
            sec_label = sec_info.get("label", sec_key)
            sec_total = sec_stat.get("total", 0)
            sec_closed = sec_stat.get("closed", 0)
            close_label = "폐쇄" if sec_key == "본지점" else "해지"
            section_cells += f"""
                <td style="width:33%;vertical-align:top;">
                    <div style="padding:16px 12px;text-align:center;border-radius:10px;background:{sec_bg};border:1px solid {sec_accent}20;">
                        <div style="font-size:20px;margin-bottom:4px;">{sec_icon}</div>
                        <div style="color:{sec_accent};font-size:13px;font-weight:700;margin-bottom:8px;">{sec_label}</div>
                        <div style="color:{sec_accent};font-size:28px;font-weight:800;line-height:1;">{sec_total:,}</div>
                        <div style="color:#94A3B8;font-size:11px;margin-top:6px;">{close_label} {sec_closed:,}개</div>
                    </div>
                </td>
            """
        section_cards_html = f"""
        <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;margin:0 0 10px 0;overflow:hidden;">
            <div style="padding:14px 18px;border-bottom:1px solid #F0F0F0;">
                <div style="display:inline-block;width:4px;height:16px;background:#6D28D9;border-radius:2px;vertical-align:middle;margin-right:10px;">&#8203;</div>
                <span style="font-size:15px;font-weight:700;color:#1E293B;vertical-align:middle;">섹션별 회선 현황</span>
            </div>
            <div style="padding:16px 12px;">
                <table cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:separate;border-spacing:10px 0;">
                    <tr>{section_cells}</tr>
                </table>
            </div>
        </div>
        """

    # ===== 섹션 3: 점포구분별 바 차트 =====
    max_count = max(by_branch.values()) if by_branch and max(by_branch.values()) > 0 else 1
    bar_rows = ""
    for bt in BRANCH_TYPES:
        count = by_branch.get(bt, 0)
        bar_width_pct = max(int((count / max_count) * 100), 2) if count > 0 else 0
        color = bar_colors.get(bt, "#3282B8")
        pct_of_total = (count / total_count * 100) if total_count > 0 else 0
        bar_rows += f"""
        <tr>
            <td style="padding:8px 12px;font-size:13px;color:#1E293B;font-weight:500;width:15%;border:none;white-space:nowrap;">{bt}</td>
            <td style="padding:8px 4px;width:65%;border:none;">
                <div style="background:{color};width:{bar_width_pct}%;height:28px;border-radius:4px;min-width:4px;"></div>
            </td>
            <td style="padding:8px 12px;font-size:13px;color:#1E293B;font-weight:600;width:10%;text-align:right;border:none;">{count:,}</td>
            <td style="padding:8px 12px;font-size:12px;color:#94A3B8;width:10%;text-align:right;border:none;">{pct_of_total:.1f}%</td>
        </tr>
        """

    chart_html = f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;margin:0 0 10px 0;overflow:hidden;">
        <div style="padding:14px 18px;border-bottom:1px solid #F0F0F0;">
            <div style="display:inline-block;width:4px;height:16px;background:{c['primary_end']};border-radius:2px;vertical-align:middle;margin-right:10px;">&#8203;</div>
            <span style="font-size:15px;font-weight:700;color:#1E293B;vertical-align:middle;">점포구분별 회선 현황</span>
        </div>
        <div style="padding:16px 12px;">
            <table cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;">
                {bar_rows}
            </table>
            <div style="text-align:right;padding:8px 12px 0 0;font-size:12px;color:#94A3B8;">총 {total_count:,}개 지점</div>
        </div>
    </div>
    """

    # ===== 섹션 4: 월간 변동이력 =====
    # 작업구분별 요약 배지
    work_badges = ""
    if by_work:
        for wt, cnt in sorted(by_work.items(), key=lambda x: x[1], reverse=True):
            badge_style = _get_work_type_badge(wt)
            work_badges += f'{badge_style} <span style="font-size:12px;color:#64748B;margin-right:12px;">{cnt}건</span>'
    else:
        work_badges = '<span style="font-size:13px;color:#94A3B8;">변동 내역 없음</span>'

    # 최근 변동 테이블 (최대 10건)
    changes_table_rows = ""
    if not changes_list.empty:
        recent = changes_list.iloc[::-1].head(10)
        for idx, row in recent.iterrows():
            시각 = str(row.get("변경시각", ""))
            if len(시각) >= 10:
                시각 = 시각[5:10]  # MM-DD
            점번 = str(row.get("점번", ""))
            지점명 = str(row.get("지점명", ""))
            전용회선 = str(row.get("전용회선", ""))
            비즈광랜 = str(row.get("비즈광랜", ""))
            작업구분 = str(row.get("작업구분", ""))
            변경요약 = str(row.get("변경 요약", ""))
            bg = "#FFFFFF" if idx % 2 == 0 else "#FAFBFC"
            changes_table_rows += f"""
            <tr style="background:{bg};">
                <td style="padding:10px 12px;font-size:12px;color:#64748B;border:none;border-bottom:1px solid #F1F5F9;">{시각}</td>
                <td style="padding:10px 12px;font-size:13px;color:#1E293B;border:none;border-bottom:1px solid #F1F5F9;">{점번}</td>
                <td style="padding:10px 12px;font-size:13px;color:#1E293B;font-weight:500;border:none;border-bottom:1px solid #F1F5F9;">{지점명}</td>
                <td style="padding:10px 12px;font-size:12px;color:#475569;border:none;border-bottom:1px solid #F1F5F9;">{전용회선}</td>
                <td style="padding:10px 12px;font-size:12px;color:#475569;border:none;border-bottom:1px solid #F1F5F9;">{비즈광랜}</td>
                <td style="padding:10px 12px;font-size:12px;border:none;border-bottom:1px solid #F1F5F9;">{_get_work_type_badge(작업구분)}</td>
                <td style="padding:10px 12px;font-size:12px;color:#64748B;border:none;border-bottom:1px solid #F1F5F9;">{변경요약}</td>
            </tr>
            """
        changes_table = f"""
        <table cellpadding="0" cellspacing="0" border="0" style="width:100%;border-collapse:collapse;margin-top:12px;">
            <tr style="background:#F1F5F9;">
                <th style="padding:10px 12px;font-size:12px;color:#64748B;font-weight:600;text-align:left;border:none;">일자</th>
                <th style="padding:10px 12px;font-size:12px;color:#64748B;font-weight:600;text-align:left;border:none;">점번</th>
                <th style="padding:10px 12px;font-size:12px;color:#64748B;font-weight:600;text-align:left;border:none;">지점명</th>
                <th style="padding:10px 12px;font-size:12px;color:#64748B;font-weight:600;text-align:left;border:none;">전용회선</th>
                <th style="padding:10px 12px;font-size:12px;color:#64748B;font-weight:600;text-align:left;border:none;">비즈광랜</th>
                <th style="padding:10px 12px;font-size:12px;color:#64748B;font-weight:600;text-align:left;border:none;">작업구분</th>
                <th style="padding:10px 12px;font-size:12px;color:#64748B;font-weight:600;text-align:left;border:none;">변경요약</th>
            </tr>
            {changes_table_rows}
        </table>
        """
    else:
        changes_table = '<p style="color:#94A3B8;font-size:13px;text-align:center;padding:20px 0;">해당 기간 변동 내역이 없습니다.</p>'

    changes_html = f"""
    <div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;margin:0 0 10px 0;overflow:hidden;">
        <div style="padding:14px 18px;border-bottom:1px solid #F0F0F0;">
            <div style="display:inline-block;width:4px;height:16px;background:#EA580C;border-radius:2px;vertical-align:middle;margin-right:10px;">&#8203;</div>
            <span style="font-size:15px;font-weight:700;color:#1E293B;vertical-align:middle;">월간 변동이력</span>
            <span style="font-size:13px;color:#94A3B8;margin-left:8px;">{period_str}</span>
        </div>
        <div style="padding:16px 18px;">
            <div style="margin-bottom:4px;">{work_badges}</div>
            {changes_table}
        </div>
    </div>
    """

    # ===== 섹션 5: 푸터 =====
    footer_html = f"""
    <p style="color:#94A3B8;font-size:11px;margin:24px 0;text-align:center;">
        본 레포트는 KB 회선관리 시스템에서 자동 생성되었습니다. | {period_str} 레포트
    </p>
    """

    # ===== 전체 조합 =====
    html_body = f"""
    <div style="width:100%;background:#F0F2F5;padding:20px 0;margin:0;font-family:{font_family};">
      <div style="max-width:800px;margin:0 auto;padding:0;">
        {header_html}
        {cards_html}
        {section_cards_html}
        {chart_html}
        {changes_html}
        {footer_html}
      </div>
    </div>
    """

    return html_body
