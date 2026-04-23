"""
Sidebar Navigation Component
"""

import streamlit as st

from config.themes import T, get_logo_html
from config.constants import NAV_PAGES


def render_sidebar():
    """Render the sidebar with logo, theme toggle, and navigation."""
    with st.sidebar:
        # Logo
        st.markdown(
            f"""
            <div style="padding:16px 8px 24px;border-bottom:1px solid {T['border']};margin-bottom:20px;text-align:center;">
                {get_logo_html(30)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Theme Toggle
        theme_label = "☀️ Light Mode" if st.session_state.theme == "dark" else "🌙 Dark Mode"
        if st.button(theme_label, key="theme_toggle", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Navigation Label
        st.markdown(
            f'<div style="font-size:0.68rem;color:{T["muted"]};text-transform:uppercase;letter-spacing:.1em;padding:0 4px;margin-bottom:8px">Navigation</div>',
            unsafe_allow_html=True,
        )

        # Navigation Buttons
        for icon, label, key in NAV_PAGES:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(
                    f'<div style="font-size:1.1rem;padding-top:4px;">{icon}</div>',
                    unsafe_allow_html=True
                )
            with col2:
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.session_state.active_page = key
                    st.rerun()

        # Footer
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="border-top:1px solid {T['border']};padding-top:16px;text-align:center;">
                <div style="font-size:0.7rem;color:{T['muted']}">Analysis Hub</div>
                <div style="font-size:0.65rem;color:{T['muted']};margin-top:2px;opacity:.6">Created by Eslam Hany ❤️</div>
            </div>
            """,
            unsafe_allow_html=True,
        )