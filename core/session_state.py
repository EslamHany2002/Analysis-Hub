"""
Session State Management
"""

import streamlit as st


def init_session_state():
    """Initialize all session state variables with defaults."""
    defaults = {
        "theme": "dark",
        "active_page": "home",
        "scheduler_instructors": {},
        "scheduler_file_loaded": False,
        # Team Performance state
        "team_data": None,
        "team_file_loaded": False,
        # B2C state
        "b2c_data": None,
        "b2c_file_loaded": False,
        # Bookings state
        "bookings_data": None,
        "bookings_file_loaded": False,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value