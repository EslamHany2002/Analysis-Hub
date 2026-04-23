"""
Home / Landing Page
"""

import streamlit as st

from config.themes import T, get_logo_html
from config.constants import DASHBOARD_CARDS
from ui.components import card_metric


def _get_card_html(card):
    """Generate HTML for a dashboard card."""
    color = card.get("color", T.get(card["color_key"], T["accent"]))
    
    tags_html = "".join(
        f'<span style="background:{color}18;color:{color};border:1px solid {color}44;'
        f'border-radius:999px;padding:3px 10px;font-size:.72rem;margin:2px;display:inline-block;'
        f'font-family:DM Mono,monospace;">{t}</span>'
        for t in card["tags"]
    )
    
    return f"""
        <div style="background:{T['card_grad']};border:1px solid {T['border']};border-top:3px solid {color};
                    border-radius:16px;padding:24px 24px 20px;margin-bottom:20px;box-shadow:0 4px 20px rgba(0,0,0,.08);height:100%;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="font-size:1.8rem;width:48px;height:48px;background:{color}18;border-radius:12px;
                            display:flex;align-items:center;justify-content:center;">{card['icon']}</div>
                <div style="font-family:'Kalam',cursive;font-size:1.2rem;font-weight:700;color:{T['text']};">{card['title']}</div>
            </div>
            <p style="font-size:.95rem;color:{T['muted']};line-height:1.65;margin:0 0 16px;font-family:'Almarai',sans-serif;">{card['desc']}</p>
            <div style="margin-bottom:20px;">{tags_html}</div>
        </div>
    """


def render_home():
    """Render the home/landing page."""
    hero_text_color = "#ffffff" if st.session_state.theme == "dark" else T["text"]
    hero_sub_color = "#a5b4fc" if st.session_state.theme == "dark" else T["accent"]

    # Hero Section
    st.markdown(
        f"""
        <div style="background:{T['hero_grad']};border:1px solid {T['border']};border-radius:24px;
                    padding:64px 56px 56px;margin-bottom:32px;position:relative;overflow:hidden;
                    box-shadow:0 20px 60px rgba(99,102,241,.15);">
            <div style="position:absolute;top:-60px;right:-60px;width:280px;height:280px;border-radius:50%;background:{T['accent']}15;"></div>
            <div style="position:absolute;bottom:-80px;right:120px;width:200px;height:200px;border-radius:50%;background:{T['accent2']}10;"></div>
            <div style="position:relative;z-index:1;">
                <div style="margin-bottom:24px;">{get_logo_html(72)}</div>
                <h1 style="font-family:'Kalam',cursive;font-size:3rem;font-weight:700;color:{hero_text_color};margin:0 0 12px;line-height:1.1;letter-spacing:-.02em;">
                    Analysis Hub
                </h1>
                <p style="font-size:1.1rem;color:{hero_sub_color};margin:0 0 32px;max-width:560px;line-height:1.65;font-family:'Almarai',sans-serif;">
                    Unified intelligence platform for session reviews, team performance,
                    instructor scheduling, and B2C feedback — all in one place.
                </p>
                <div style="display:flex;gap:12px;flex-wrap:wrap;">
                    <span style="background:{T['accent']}22;color:{T['accent2']};border:1px solid {T['accent']}44;border-radius:999px;padding:6px 16px;font-size:.82rem;font-family:'DM Mono',monospace;">4 Dashboards</span>
                    <span style="background:{T['green']}22;color:{T['green']};border:1px solid {T['green']}44;border-radius:999px;padding:6px 16px;font-size:.82rem;font-family:'DM Mono',monospace;">2 Themes</span>
                    <span style="background:{T['accent2']}22;color:{T['accent2']};border:1px solid {T['accent2']}44;border-radius:999px;padding:6px 16px;font-size:.82rem;font-family:'DM Mono',monospace;">Real-time Filters</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Section Title
    st.markdown(
        f'<h2 style="font-family:Kalam,cursive;font-size:1.6rem;color:{T["text"]};margin-bottom:24px;">📂 Available Dashboards</h2>',
        unsafe_allow_html=True,
    )

    # Dashboard Cards Grid (2x2)
    col1, col2 = st.columns(2, gap="large")
    
    for i, card in enumerate(DASHBOARD_CARDS):
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            st.markdown(_get_card_html(card), unsafe_allow_html=True)
            if st.button(
                f"Open {card['title']} →",
                key=f"home_btn_{card['key']}",
                use_container_width=True
            ):
                st.session_state.active_page = card["key"]
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Bottom Stats
    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("4", "Active Dashboards", T["accent"], "📊"),
        ("2", "Theme Options", T["green"], "🎨"),
        ("∞", "Data Uploads", T["amber"], "📂"),
        ("AI", "Sentiment Engine", T["red"], "🤖"),
    ]
    for col, (val, lbl, clr, ico) in zip([s1, s2, s3, s4], stats):
        card_metric(col, val, lbl, clr, ico)