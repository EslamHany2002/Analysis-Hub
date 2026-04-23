"""
Budget Calculator Page
Calculates hourly rates for Budget, L&D, Full Time, and TA categories
with full dark/light theme support.
"""

import streamlit as st
from config.themes import T
from ui.components import render_page_header


def _calc_card(title, icon, color, fields, results):
    """Render a styled calculator card."""
    results_html = ""
    for label, value in results:
        results_html += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid {T["border"]};"><span style="font-family:Almarai,sans-serif;font-size:0.82rem;color:{T["muted"]};">{label}</span><span style="font-family:DM Mono,monospace;font-size:1.05rem;font-weight:700;color:{color};">{value}</span></div>'
    
    no_results = f'<div style="color:{T["muted"]};font-size:0.85rem;padding:10px 0;">Enter values above to see results</div>'
    final_html = results_html if results_html else no_results

    st.markdown(f'<div style="background:{T["surface"]};border:1px solid {T["border"]};border-top:4px solid {color};border-radius:18px;padding:24px 22px 18px;box-shadow:0 4px 20px rgba(0,0,0,.07);height:100%;margin-bottom:10px;"><div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;"><div style="font-size:1.6rem;width:44px;height:44px;background:{color}18;border-radius:12px;display:flex;align-items:center;justify-content:center;">{icon}</div><div style="font-family:Kalam,cursive;font-size:1.25rem;font-weight:700;color:{T["text"]};">{title}</div></div><div style="margin-top:4px;">{final_html}</div></div>', unsafe_allow_html=True)


def _summary_card(items):
    """Render a summary card showing all calculated rates."""
    rows_html = ""
    for label, rate, color in items:
        rows_html += f'<div style="display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid {T["border"]};border-left:4px solid {color};"><span style="font-family:Almarai,sans-serif;font-size:0.88rem;color:{T["text2"]};">{label}</span><span style="font-family:DM Mono,monospace;font-size:1.1rem;font-weight:800;color:{color};">{rate}</span></div>'

    st.markdown(f'<div style="background:{T["surface"]};border:1px solid {T["border"]};border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.07);"><div style="padding:16px 20px;background:{T["accent"]}15;border-bottom:1px solid {T["border"]};"><span style="font-family:Kalam,cursive;font-size:1.1rem;font-weight:700;color:{T["text"]};">📊 Hourly Rates Summary</span></div>{rows_html}</div>', unsafe_allow_html=True)


def _kpi_box(label, value, color, icon):
    return f'<div style="background:{T["surface"]};border:1px solid {T["border"]};border-left:5px solid {color};border-radius:14px;padding:16px 20px;display:flex;align-items:center;gap:14px;box-shadow:0 2px 10px rgba(0,0,0,.05);"><div style="font-size:1.8rem;">{icon}</div><div><div style="font-family:DM Mono,monospace;font-size:1.5rem;font-weight:800;color:{color};line-height:1.1;">{value}</div><div style="font-family:Almarai,sans-serif;font-size:0.78rem;color:{T["muted"]};margin-top:3px;">{label}</div></div></div>'


def render_budget():
    """Render the Budget Calculator dashboard."""
    render_page_header(
        "Budget Calculator",
        "Calculate hourly rates and total costs across Budget, L&D, Full Time, and TA categories.",
        "💰"
    )

    # ══════════════════════════════════════════════════════════════════
    # Input Section
    # ══════════════════════════════════════════════════════════════════
    # ══════════════════════════════════════════════════════════════════
    # Input Section
    # ══════════════════════════════════════════════════════════════════
    st.markdown(
        f'<div class="section-title">⚙️ Input Parameters</div>',
        unsafe_allow_html=True
    )

    # عملنا أعمدة: 4 للكروت، و 3 فاصلة رفيعة بينهم
    col_budget, sep1, col_ld, sep2, col_ft, sep3, col_ta = st.columns((4, 0.2, 4, 0.2, 4, 0.2, 4))

    # دالة مساعدة لرسم الخط الفاصل
    def _draw_separator():
        st.markdown(
            f'<div style="height: 110px; width: 1px; background: {T["border2"]}; margin: 28px auto 0 auto;"></div>',
            unsafe_allow_html=True
        )

    # رسم الخطوط في الأعمدة الفاصلة
    with sep1:
        _draw_separator()
    with sep2:
        _draw_separator()
    with sep3:
        _draw_separator()

    # ── Budget ──
    with col_budget:
        st.markdown(f'<div style="font-family:Kalam,cursive;font-size:1rem;color:{T["accent"]};margin-bottom:8px;">💼 Budget</div>', unsafe_allow_html=True)
        rate = st.number_input("Rate", min_value=0.0, value=0.0, step=10.0, key="budget_rate", format="%.2f")
        hours = st.number_input("Hours", min_value=0.0, value=0.0, step=1.0, key="budget_hours", format="%.1f")

    # ── L&D ──
    with col_ld:
        st.markdown(f'<div style="font-family:Kalam,cursive;font-size:1rem;color:{T["green"]};margin-bottom:8px;">📚 L&D</div>', unsafe_allow_html=True)
        salary_ld = st.number_input("Salary", min_value=0.0, value=0.0, step=100.0, key="ld_salary", format="%.2f")
        hours_month_ld = st.number_input("Monthly Hours", min_value=0.0, value=0.0, step=1.0, key="ld_hours", format="%.1f")

    # ── Full Time ──
    with col_ft:
        st.markdown(f'<div style="font-family:Kalam,cursive;font-size:1rem;color:{T["amber"]};margin-bottom:8px;">🏢 Full Time</div>', unsafe_allow_html=True)
        full_time_input = st.number_input("Input", min_value=0.0, value=0.0, step=100.0, key="ft_input", format="%.2f")
        hours_month_ft = st.number_input("Monthly Hours", min_value=0.0, value=0.0, step=1.0, key="ft_hours", format="%.1f")

    # ── TA ──
    with col_ta:
        st.markdown(f'<div style="font-family:Kalam,cursive;font-size:1rem;color:{T["red"]};margin-bottom:8px;">🎓 TA</div>', unsafe_allow_html=True)
        salary_ta = st.number_input("Salary", min_value=0.0, value=0.0, step=100.0, key="ta_salary", format="%.2f")
        hours_month_ta = st.number_input("Monthly Hours", min_value=0.0, value=0.0, step=1.0, key="ta_hours", format="%.1f")
    # ══════════════════════════════════════════════════════════════════
    # Calculations
    # ══════════════════════════════════════════════════════════════════
    budget_total = rate * hours
    ld_total = salary_ld * 1.3 * 0.6
    ld_hourly = ld_total / hours_month_ld if hours_month_ld else 0
    ft_total = full_time_input * 1.3
    ft_hourly = ft_total / hours_month_ft if hours_month_ft else 0
    ta_total = salary_ta * 1.3 * 0.25
    ta_hourly = ta_total / hours_month_ta if hours_month_ta else 0

    # ══════════════════════════════════════════════════════════════════
    # KPI Row — كرتين في الصف
    # ══════════════════════════════════════════════════════════════════
    st.markdown(f'<div class="section-title">📈 Summary KPIs</div>', unsafe_allow_html=True)

    k1, k2 = st.columns(2)
    with k1:
        st.markdown(_kpi_box("Budget Total", f"{budget_total:,.2f}", T["accent"], "💼"), unsafe_allow_html=True)
    with k2:
        st.markdown(_kpi_box("L&D Hourly Rate", f"{ld_hourly:,.2f}", T["green"], "📚"), unsafe_allow_html=True)

    k3, k4 = st.columns(2)
    with k3:
        st.markdown(_kpi_box("Full Time Hourly Rate", f"{ft_hourly:,.2f}", T["amber"], "🏢"), unsafe_allow_html=True)
    with k4:
        st.markdown(_kpi_box("TA Hourly Rate", f"{ta_hourly:,.2f}", T["red"], "🎓"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # Detail Cards — كرتين في الصف
    # ══════════════════════════════════════════════════════════════════
    st.markdown(f'<div class="section-title">🧮 Calculation Details</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        _calc_card("Budget", "💼", T["accent"], [], [("Rate", f"{rate:,.2f}"), ("Hours", f"{hours:,.1f}"), ("Budget Total", f"{budget_total:,.2f}")])
    with c2:
        _calc_card("L&D", "📚", T["green"], [], [("Salary", f"{salary_ld:,.2f}"), ("× 1.3 × 0.6 =", f"{ld_total:,.2f}"), ("Monthly Hours", f"{hours_month_ld:,.1f}"), ("Hourly Rate", f"{ld_hourly:,.2f}")])

    c3, c4 = st.columns(2)
    with c3:
        _calc_card("Full Time", "🏢", T["amber"], [], [("Input", f"{full_time_input:,.2f}"), ("× 1.3 =", f"{ft_total:,.2f}"), ("Monthly Hours", f"{hours_month_ft:,.1f}"), ("Hourly Rate", f"{ft_hourly:,.2f}")])
    with c4:
        _calc_card("TA", "🎓", T["red"], [], [("Salary", f"{salary_ta:,.2f}"), ("× 1.3 × 0.25 =", f"{ta_total:,.2f}"), ("Monthly Hours", f"{hours_month_ta:,.1f}"), ("Hourly Rate", f"{ta_hourly:,.2f}")])

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # Summary Table
    # ══════════════════════════════════════════════════════════════════
    _summary_card([
        ("💼 Budget Total", f"{budget_total:,.2f}", T["accent"]),
        ("📚 L&D — Calculated Value", f"{ld_total:,.2f}", T["green"]),
        ("📚 L&D — Hourly Rate", f"{ld_hourly:,.2f}", T["green"]),
        ("🏢 Full Time — Calculated Value", f"{ft_total:,.2f}", T["amber"]),
        ("🏢 Full Time — Hourly Rate", f"{ft_hourly:,.2f}", T["amber"]),
        ("🎓 TA — Calculated Value", f"{ta_total:,.2f}", T["red"]),
        ("🎓 TA — Hourly Rate", f"{ta_hourly:,.2f}", T["red"]),
    ])