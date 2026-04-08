# -*- coding: utf-8 -*-
"""
메인 앱 CSS 스타일
"""


def get_main_css():
    """메인 CSS 반환"""
    return """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css">
<style>
.ti { font-size: 1.25rem; vertical-align: middle; }
.ti-sm { font-size: 1rem; }
.ti-lg { font-size: 1.5rem; }
.stApp { background-color: #ffffff; }
section[data-testid="stSidebar"] { background-color: transparent !important; border-right: none !important; }
section[data-testid="stSidebar"] > div:first-child { background-color: transparent !important; padding-top: 0 !important; }
.sidebar-container { background: transparent; padding: 0; }
.sidebar-brand { display: flex; align-items: center; gap: 12px; padding: 1.25rem 1rem; margin-bottom: 0.5rem; }
.sidebar-brand-logo { width: 40px; height: 40px; background: linear-gradient(135deg, #066fd1 0%, #4263eb 100%); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem; }
.sidebar-brand-title { font-size: 1rem; font-weight: 600; color: #1e293b; }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 0.625rem 1rem; margin: 2px 0.5rem; border-radius: 6px; color: #64748b; text-decoration: none; font-size: 0.875rem; font-weight: 500; cursor: pointer; transition: all 0.15s ease; }
.nav-item:hover { background-color: rgba(6, 111, 209, 0.08); color: #066fd1; }
.nav-item.active { background-color: rgba(6, 111, 209, 0.1); color: #066fd1; font-weight: 600; }
.nav-item i { font-size: 1.25rem; width: 24px; text-align: center; }
.sidebar-user { margin-top: auto; padding: 1rem; border-top: 1px solid #e2e8f0; }
.user-box { display: flex; align-items: center; gap: 12px; padding: 0.75rem; background: #ffffff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.user-avatar { width: 40px; height: 40px; background: linear-gradient(135deg, #066fd1 0%, #4263eb 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 1rem; }
.user-details { flex: 1; }
.user-name { font-weight: 600; font-size: 0.875rem; color: #1e293b; }
.user-role { font-size: 0.75rem; color: #64748b; }
.main-content { padding: 0; }
.page-header { background: #ffffff; padding: 1.25rem 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.page-pretitle { font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; }
.page-title { font-size: 1.5rem; font-weight: 600; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); margin-bottom: 1.5rem; }
.card-header { padding: 1rem 1.25rem; border-bottom: 1px solid #e2e8f0; background: transparent; }
.card-title { font-size: 1rem; font-weight: 600; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.card-body { padding: 1.25rem; }
.stButton > button { background-color: #066fd1; color: white; border: none; border-radius: 6px; padding: 0.5rem 1rem; font-weight: 500; transition: all 0.15s ease; }
.stButton > button:hover { background-color: #0559a8; box-shadow: 0 2px 8px rgba(6,111,209,0.25); }
.stFormSubmitButton > button { background: #066fd1; color: white; border: none; border-radius: 6px; padding: 0.625rem 1.25rem; font-weight: 500; }
.stTextInput > label, .stSelectbox > label, .stTextArea > label, .stDateInput > label { color: #334155; font-weight: 500; font-size: 0.875rem; }
[data-baseweb="input"] { border: 2px solid #cbd5e1 !important; border-radius: 8px !important; background: #f1f5f9 !important; transition: border-color 0.15s ease, box-shadow 0.15s ease !important; }
[data-baseweb="input"]:focus-within { border-color: #066fd1 !important; box-shadow: 0 0 0 3px rgba(6,111,209,0.2) !important; background: #ffffff !important; }
[data-baseweb="base-input"] { border: none !important; box-shadow: none !important; background: transparent !important; }
[data-baseweb="input"] input { border: none !important; box-shadow: none !important; outline: none !important; background: transparent !important; }
[data-baseweb="input"] input:focus { border: none !important; box-shadow: none !important; outline: none !important; }
[data-baseweb="input"] button { border: none !important; box-shadow: none !important; background: transparent !important; color: #64748b !important; }
.stTextInput input:disabled { background-color: #f8fafc !important; color: #64748b; }
[data-baseweb="select"] > div:first-child { border: 2px solid #cbd5e1 !important; border-radius: 8px !important; background: #f1f5f9 !important; transition: border-color 0.15s ease !important; }
[data-baseweb="select"] > div:first-child:hover { border-color: #066fd1 !important; }
[data-baseweb="select"]:focus-within > div:first-child { border-color: #066fd1 !important; box-shadow: 0 0 0 3px rgba(6,111,209,0.2) !important; }
.stTextArea > div > div > textarea { border: 2px solid #cbd5e1 !important; border-radius: 8px !important; background: #f1f5f9 !important; transition: border-color 0.15s ease !important; }
.stTextArea > div > div > textarea:hover { border-color: #066fd1 !important; }
.stTextArea > div > div > textarea:focus { border-color: #066fd1 !important; box-shadow: 0 0 0 3px rgba(6,111,209,0.2) !important; background: #ffffff !important; outline: none !important; }
.stDateInput [data-baseweb="input"] { border: 2px solid #cbd5e1 !important; border-radius: 8px !important; background: #f1f5f9 !important; }
.section-title { font-size: 1rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
[data-testid="stMetricValue"] { font-size: 1.75rem; font-weight: 700; color: #1e293b; }
[data-testid="stMetricLabel"] { font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
.stDataFrame { border: 1px solid #e2e8f0; border-radius: 8px; }
.stSuccess { background-color: #ecfdf5; border-left: 4px solid #10b981; color: #065f46; }
.stError { background-color: #fef2f2; border-left: 4px solid #ef4444; color: #991b1b; }
.stWarning { background-color: #fffbeb; border-left: 4px solid #f59e0b; color: #92400e; }
.stInfo { background-color: #eff6ff; border-left: 4px solid #3b82f6; color: #1e40af; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }
[data-testid="stForm"] { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1.5rem; }
section[data-testid="stSidebar"] .stButton > button { width: 100%; text-align: left; background: transparent; color: #64748b; border: none; padding: 0.625rem 1rem; margin: 2px 0; border-radius: 6px; font-weight: 500; justify-content: flex-start; transition: all 0.15s ease; }
section[data-testid="stSidebar"] .stButton > button:hover { background-color: rgba(6, 111, 209, 0.08); color: #066fd1; }
section[data-testid="stSidebar"] .stButton > button[kind="primary"] { background: linear-gradient(135deg, rgba(6, 111, 209, 0.15) 0%, rgba(66, 99, 235, 0.12) 100%) !important; color: #066fd1 !important; font-weight: 600 !important; border-left: 3px solid #066fd1 !important; box-shadow: 0 1px 3px rgba(6, 111, 209, 0.1) !important; }
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, rgba(6, 111, 209, 0.22) 0%, rgba(66, 99, 235, 0.18) 100%) !important; }
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] { background: transparent !important; color: #64748b !important; border: none !important; border-left: 3px solid transparent !important; }
section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover { background-color: rgba(6, 111, 209, 0.06) !important; color: #066fd1 !important; border-left: 3px solid rgba(6, 111, 209, 0.3) !important; }
section[data-testid="stSidebar"] .stExpander { border: none !important; background: transparent !important; margin-bottom: 4px; }
section[data-testid="stSidebar"] .stExpander > details { border: 1px solid #e2e8f0 !important; border-radius: 8px !important; background: #ffffff !important; overflow: hidden; }
section[data-testid="stSidebar"] .stExpander > details > summary { padding: 12px 16px !important; font-weight: 600 !important; font-size: 0.9rem !important; color: #1e293b !important; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important; border-bottom: 1px solid #e2e8f0; transition: all 0.15s ease; }
section[data-testid="stSidebar"] .stExpander > details > summary:hover { background: linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%) !important; color: #066fd1 !important; }
section[data-testid="stSidebar"] .stExpander > details[open] > summary { background: linear-gradient(135deg, #066fd1 0%, #4263eb 100%) !important; color: #ffffff !important; border-bottom: none; }
section[data-testid="stSidebar"] .stExpander > details > div[data-testid="stExpanderDetails"] { padding: 8px 4px !important; background: #fafbfc; }
.logout-button button { background: #f1f5f9 !important; color: #64748b !important; border: 1px solid #e2e8f0 !important; }
.logout-button button:hover { background: #fee2e2 !important; color: #dc2626 !important; border-color: #fecaca !important; }
</style>"""
