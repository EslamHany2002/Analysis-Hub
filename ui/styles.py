"""
Global CSS Styles Injection
"""

import streamlit as st

from config.themes import T


def inject_global_css():
    """Inject global CSS styles into the Streamlit app."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Almarai:wght@300;400;700;800&family=Kalam:wght@300;400;700&family=DM+Mono:wght@300;400;500&display=swap');

/* ══════════════════════════════════════════════════════════════════
   BASE STYLES
   ══════════════════════════════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {{
    background: {T['bg']} !important;
    color: {T['text']} !important;
    font-family: 'Almarai', sans-serif !important;
}}

h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    font-family: 'Kalam', cursive !important;
}}

/* ══════════════════════════════════════════════════════════════════
   إخفاء الهيدر العلوي بالكامل
   ══════════════════════════════════════════════════════════════════ */
header {{
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    top: -100px !important;  <!-- الخطأ هنا -->
}}

[data-testid="stToolbar"] {{
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}}

#MainMenu {{
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}}

[data-testid="stHeader"] {{
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}}

footer {{
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}}

[data-testid="stDecoration"] {{
    display: none !important;
}}

/* ══════════════════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    width: 210px !important;
    min-width: 210px !important;
    max-width: 210px !important;
    background: {T['nav_grad']} !important;
    border-right: 1px solid {T['border']} !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
    /* الأسرار السحرية الثلاثة ليمنع الإخفاء: */
    transform: none !important; 
    position: relative !important;
    transition: none !important;
}}

[data-testid="stSidebar"] > div:first-child {{
    width: 210px !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

[data-testid="stSidebar"] * {{ color: {T['text']} !important; }}



/* ══════════════════════════════════════════════════════════════════
   إخفاء خانة البحث في الـ Sidebar
   ══════════════════════════════════════════════════════════════════ */
[data-testid="stSidebarSearch"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}}

/* إخفاء أي عنصر بحث تاني */
[data-testid="stSearch"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
}}

/* إخفاء الـ app default navigation item */
[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    max-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
}}

/* ══════════════════════════════════════════════════════════════════
   إزالة زرار إخفاء السايدبار نهائياً (بكل طرقه)
   ══════════════════════════════════════════════════════════════════ */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="header"],
[data-testid="stSidebar"] > div:first-child > div > button {{
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
    overflow: hidden !important;
    position: absolute !important;
    top: -9999px !important;
}}
/* ══════════════════════════════════════════════════════════════════
   BUTTONS
   ══════════════════════════════════════════════════════════════════ */
.stButton > button {{
    background: {T['accent']} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Kalam', sans-serif !important;
    font-weight: 700 !important;
    padding: 10px 18px !important;
}}

.stButton > button:hover {{
    opacity: .9 !important;
}}

[data-testid="stSidebar"] .stButton > button {{
    font-size: 0.85rem !important;
    padding: 6px 12px !important;
    margin-top: 2px !important;
    height: auto !important;
}}

/* ══════════════════════════════════════════════════════════════════
   INPUTS
   ══════════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"],
[data-testid="stDataFrame"],
[data-testid="stMetric"] {{
    border-radius: 12px !important;
    overflow: hidden !important;
}}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
textarea,
[data-baseweb="select"] > div,
[data-testid="stMultiSelect"] > div {{
    background: {T['input_bg']} !important;
    color: {T['text']} !important;
    border: 1px solid {T['border2']} !important;
    border-radius: 8px !important;
}}

[data-baseweb="menu"] {{
    background: {T['surface']} !important;
    border: 1px solid {T['border2']} !important;
}}

[data-baseweb="menu"] li {{
    color: {T['text']} !important;
    background: {T['surface']} !important;
}}

[data-baseweb="menu"] li:hover {{
    background: {T['border']} !important;
}}

/* ══════════════════════════════════════════════════════════════════
   TABS
   ══════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    gap: .5rem;
    background: {T['surface']} !important;
    padding: .45rem;
    border-radius: 12px;
    border: 1px solid {T['border']};
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 9px !important;
    font-weight: 600 !important;
    color: {T['muted']} !important;
    font-family: 'Syne', sans-serif !important;
}}

.stTabs [aria-selected="true"] {{
    background: {T['accent']} !important;
    color: #fff !important;
}}

/* ══════════════════════════════════════════════════════════════════
   KPI CARDS
   ══════════════════════════════════════════════════════════════════ */
.kpi-card {{
    background: {T['surface']};
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, .06);
    border-left: 4px solid {T['accent']};
    position: relative;
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
    border: 1px solid {T['border']};
}}

.kpi-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, .10);
}}

.kpi-card.green {{ border-left-color: {T['green']}; }}
.kpi-card.amber {{ border-left-color: #D97706; }}
.kpi-card.red {{ border-left-color: {T['red']}; }}
.kpi-card.purple {{ border-left-color: #7C3AED; }}
.kpi-card.teal {{ border-left-color: #0D9488; }}

.kpi-icon {{ font-size: 1.5rem; margin-bottom: .35rem; }}
.kpi-value {{ font-size: 2rem; font-weight: 700; color: {T['text']}; line-height: 1; }}
.kpi-label {{
    font-size: .75rem;
    color: {T['muted']};
    text-transform: uppercase;
    letter-spacing: .07em;
    margin-top: .3rem;
}}
.kpi-delta {{ font-size: .75rem; color: {T['muted']}; margin-top: .2rem; }}
.kpi-bg {{
    position: absolute;
    right: -8px;
    top: -8px;
    font-size: 4.5rem;
    opacity: .06;
    color: {T['text']};
}}

/* ══════════════════════════════════════════════════════════════════
   SECTION & CHART STYLES
   ══════════════════════════════════════════════════════════════════ */
.section-title {{
    font-family: 'DM Serif Display', 'Syne', sans-serif;
    font-size: 1.2rem;
    color: {T['text']};
    padding-bottom: .5rem;
    border-bottom: 2px solid {T['border']};
    margin: 2.2rem 0 1.2rem;
}}

.chart-card {{
    background: {T['surface']};
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, .06);
    margin-bottom: .4rem;
    border: 1px solid {T['border']};
}}

.insight-box {{
    background: {T['surface']};
    border-left: 4px solid {T['accent']};
    border-radius: 0 8px 8px 8px;
    padding: .75rem 1.1rem;
    font-size: .82rem;
    color: {T['text']};
    line-height: 1.6;
    margin-bottom: 1.2rem;
    border: 1px solid {T['border']};
}}

.insight-good {{
    background: {"#F0FDF4" if st.session_state.theme == "light" else "rgba(16,185,129,.10)"};
    border-left-color: {T['green']};
    color: {T['green']};
}}

.insight-warn {{
    background: {"#FFFBEB" if st.session_state.theme == "light" else "rgba(245,158,11,.10)"};
    border-left-color: {T['amber']};
    color: {T['amber']};
}}

.fb-chip {{
    display: inline-block;
    background: {T['surface2']};
    color: {T['text']};
    border: 1px solid {T['border']};
    border-radius: 20px;
    padding: .22rem .8rem;
    font-size: .8rem;
    margin: .2rem .15rem;
}}

/* ══════════════════════════════════════════════════════════════════
   CHART EXPLANATION
   ══════════════════════════════════════════════════════════════════ */
.chart-explanation {{
    background: #F3F4F6;
    border-left: 5px solid #4F46E5;
    border-radius: 0 16px 16px 0;
    padding: 22px 28px;
    margin: 18px 0 20px 0;
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.8;
}}

.chart-explanation strong {{
    display: block;
    color: #334155;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 6px;
}}

/* ══════════════════════════════════════════════════════════════════
   SCROLLBAR
   ══════════════════════════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {T['scrollbg']}; }}
::-webkit-scrollbar-thumb {{ background: {T['scrollfg']}; border-radius: 3px; }}

</style>
""",
        unsafe_allow_html=True,
    )