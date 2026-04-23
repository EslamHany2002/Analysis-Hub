"""
Analysis Hub - Main Entry Point
Unified intelligence platform for session reviews, team performance,
instructor scheduling, and B2C feedback.
"""

import streamlit as st

from config.themes import T, init_theme
from core.session_state import init_session_state
from ui.styles import inject_global_css
from ui.sidebar import render_sidebar
from pages.home import render_home
from pages.team import render_team
from pages.b2c import render_b2c
from pages.scheduler import render_scheduler
from pages.bookings import render_bookings
from pages.budget import render_budget


def main():
    # ══════════════════════════════════════════════════════════════════
    # PAGE CONFIG - Must be first Streamlit command
    # ══════════════════════════════════════════════════════════════════
    st.set_page_config(
        page_title="DEPI Hub · Analytics Platform",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ══════════════════════════════════════════════════════════════════
    # INITIALIZATION
    # ══════════════════════════════════════════════════════════════════
    init_session_state()
    init_theme()
    inject_global_css()
    render_sidebar()

    # ══════════════════════════════════════════════════════════════════
    # ROUTER
    # ══════════════════════════════════════════════════════════════════
    page_router = {
        "home": render_home,
        "team": render_team,
        "b2c": render_b2c,
        "scheduler": render_scheduler,
        "bookings": render_bookings,
        "budget": render_budget,
    }

    active_page = st.session_state.get("active_page", "home")
    renderer = page_router.get(active_page, render_home)
    renderer()


if __name__ == "__main__":
    main()