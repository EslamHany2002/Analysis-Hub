"""
Reusable UI Components
"""

import streamlit as st
import pandas as pd

from config.themes import T
from config.constants import CHART_H, PAPER, PLOT


def safe_num(val, decimals=1, fallback=0):
    """Return a clean number, never NaN."""
    if val is None or pd.isna(val):
        return fallback
    try:
        return round(float(val), decimals)
    except (ValueError, TypeError):
        return fallback


def safe_pct_calc(num, den, decimals=1):
    """Safe percentage calculation, never NaN."""
    if den is None or pd.isna(den) or den == 0:
        return 0.0
    if num is None or pd.isna(num):
        return 0.0
    return round((num / den) * 100, decimals)


def show_info_box(text, tone="info"):
    """Display an info/warning box."""
    tone_color = {
        "info": T["accent"],
        "good": T["green"],
        "warn": T["amber"],
        "bad": T["red"],
    }.get(tone, T["accent"])
    
    st.markdown(
        f"""
        <div style="background:{T['surface']};border:1px solid {T['border']};border-left:4px solid {tone_color};
                    border-radius:12px;padding:12px 14px;margin:10px 0 16px;color:{T['text2']};font-size:.92rem;line-height:1.6;">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text):
    """Render a section title."""
    st.markdown(
        f"<h3 style='font-family:Kalam,cursive;color:{T['text']};margin:20px 0 14px'>{text}</h3>",
        unsafe_allow_html=True,
    )


def card_metric(col, value, label, color=None, icon="📊"):
    """Render a metric card."""
    color = color or T["accent"]

    html = (
        f'<div style="'
        f'background:{T["surface"]};'
        f'border:1px solid {T["border"]};'
        f'border-left:5px solid {color};'
        f'border-radius:22px;'
        f'padding:18px 20px;'
        f'min-height:92px;'
        f'width:100%;'
        f'box-sizing:border-box;'
        f'display:flex;'
        f'align-items:center;'
        f'gap:16px;'
        f'margin-bottom:14px;'
        f'overflow:hidden;'
        f'">'

        f'<div style="'
        f'font-size:2.2rem;'
        f'line-height:1;'
        f'width:52px;'
        f'min-width:52px;'
        f'display:flex;'
        f'align-items:center;'
        f'justify-content:center;'
        f'flex-shrink:0;'
        f'">{icon}</div>'

        f'<div style="'
        f'display:flex;'
        f'flex-direction:column;'
        f'justify-content:center;'
        f'align-items:flex-start;'
        f'flex:1;'
        f'min-width:0;'
        f'overflow:hidden;'
        f'">'

        f'<div style="'
        f'font-family:Almarai,sans-serif;'
        f'font-size:1.6rem;'
        f'font-weight:800;'
        f'color:{color};'
        f'line-height:1.05;'
        f'margin-bottom:6px;'
        f'white-space:nowrap;'
        f'overflow:hidden;'
        f'text-overflow:ellipsis;'
        f'width:100%;'
        f'">{value}</div>'

        f'<div style="'
        f'font-family:Kalam,cursive;'
        f'font-size:1rem;'
        f'color:{T["muted"]};'
        f'line-height:1.2;'
        f'white-space:nowrap;'
        f'overflow:hidden;'
        f'text-overflow:ellipsis;'
        f'width:100%;'
        f'">{label}</div>'

        f'</div>'
        f'</div>'
    )

    col.markdown(html, unsafe_allow_html=True)


def render_page_header(title, subtitle, icon="📊"):
    """Render a page header with title and subtitle."""
    st.markdown(
        f"""
        <div style="background:{T['card_grad']};border:1px solid {T['border']};border-radius:18px;padding:22px 24px;
                    margin-bottom:18px;box-shadow:0 10px 30px rgba(0,0,0,.08)">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
                <div>
                    <div style="font-family:Kalam,cursive;font-size:2.2rem;font-weight:700;color:{T['text']};line-height:1.1;">{title}</div>
                    <div style="margin-top:6px;color:{T['muted']};font-size:.95rem;font-family:Almarai,sans-serif;">{subtitle}</div>
                </div>
                <div style="font-size:2.4rem;opacity:.85">{icon}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_explanation(title, text):
    """Render a chart explanation box."""
    st.markdown(f"""
    <div class="chart-explanation">
        <strong>{title}</strong>
        {text}
    </div>
    """, unsafe_allow_html=True)


def plotly_layout(fig, height=CHART_H):
    """Apply consistent layout to Plotly figures."""
    grid_color = "#E5E7EB" if st.session_state.theme == "light" else "#334155"
    font = dict(family="Almarai", color=T["text"])
    
    fig.update_layout(
        height=height,
        paper_bgcolor=PAPER,
        plot_bgcolor=PLOT,
        font=font,
        margin=dict(t=55, b=25, l=10, r=10),
    )
    return fig

def kpi(col, icon, value, label, sub="", color=""):
    """Render a KPI card with background icon (original B2C style)."""
    col.markdown(f"""
    <div class="kpi-card {color}">
      <div class="kpi-bg">{icon}</div>
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-delta">{sub}</div>
    </div>
    """, unsafe_allow_html=True)