"""
Theme Management - Dark & Light mode tokens
"""

import streamlit as st

DARK = {
    "bg": "#0b0f19",
    "surface": "#111827",
    "surface2": "#0d1117",
    "border": "#1f2937",
    "border2": "#374151",
    "text": "#f9fafb",
    "text2": "#e2e8f0",
    "muted": "#6b7280",
    "accent": "#6366f1",
    "accent2": "#818cf8",
    "green": "#10b981",
    "red": "#ef4444",
    "amber": "#f59e0b",
    "scrollbg": "#111827",
    "scrollfg": "#374151",
    "offbg": "#1c1c2e",
    "offborder": "#3b3b5c",
    "offtext": "#a5b4fc",
    "input_bg": "#111827",
    "card_grad": "linear-gradient(135deg, #111827 0%, #1a2035 100%)",
    "hero_grad": "linear-gradient(135deg, #0b0f19 0%, #1a1f3a 40%, #2d2060 100%)",
    "nav_grad": "linear-gradient(180deg, #0d1117 0%, #111827 100%)",
    "sum_bg": "#111827",
    "sum_bg_alt": "#0f172a",
    "sum_row_border": "#1f2937",
    "sum_key_color": "#9ca3af",
    "sum_val_color": "#f9fafb",
}

LIGHT = {
    "bg": "#f8fafc",
    "surface": "#ffffff",
    "surface2": "#f1f5f9",
    "border": "#e2e8f0",
    "border2": "#cbd5e1",
    "text": "#0f172a",
    "text2": "#1e293b",
    "muted": "#64748b",
    "accent": "#4f46e5",
    "accent2": "#6366f1",
    "green": "#059669",
    "red": "#dc2626",
    "amber": "#d97706",
    "scrollbg": "#f1f5f9",
    "scrollfg": "#cbd5e1",
    "offbg": "#eef2ff",
    "offborder": "#a5b4fc",
    "offtext": "#4338ca",
    "input_bg": "#ffffff",
    "card_grad": "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
    "hero_grad": "linear-gradient(135deg, #eef2ff 0%, #e0e7ff 40%, #c7d2fe 100%)",
    "nav_grad": "linear-gradient(180deg, #f1f5f9 0%, #ffffff 100%)",
    "sum_bg": "#ffffff",
    "sum_bg_alt": "#f8fafc",
    "sum_row_border": "#e2e8f0",
    "sum_key_color": "#475569",
    "sum_val_color": "#0f172a",
}

T = DARK.copy()


def init_theme():
    """Update global T based on current session state theme."""
    target = LIGHT if st.session_state.theme == "light" else DARK
    T.clear()
    T.update(target)


def get_logo_html(height=48):
    """
    Generate logo HTML.
    
    Priority:
    1. assets/logo.png  (your custom logo - PUT IT HERE)
    2. Picture1.png      (root level fallback)
    3. logo.png          (root level fallback)
    4. Text fallback     (DEPI HUB text)
    """
    import base64
    import os

    # ══════════════════════════════════════════════════════
    # الأولوية الأولى: assets/logo.png (الصورة بتاعتك)
    # ══════════════════════════════════════════════════════
    custom_logo = os.path.join("assets", "logo.png")
    if os.path.exists(custom_logo):
        with open(custom_logo, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (
            f'<img src="data:image/png;base64,{b64}" '
            f'style="height:{height}px;object-fit:contain;" />'
        )

    # ══════════════════════════════════════════════════════
    # الفولبات القديمة (للتوافق)
    # ══════════════════════════════════════════════════════
    fallback_paths = ["Picture1.png", "logo.png", "company_logo.png"]
    for logo_path in fallback_paths:
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            return (
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:{height}px;object-fit:contain;" />'
            )

    # ══════════════════════════════════════════════════════
    # الفولبات النهائي: نص DEPI HUB
    # ══════════════════════════════════════════════════════
    return (
        f'<div style="font-family:Syne,sans-serif;font-size:{height // 2}px;font-weight:800;'
        f'color:{T["accent2"]};letter-spacing:-.02em;">DEPI'
        f'<span style="color:{T["accent"]};">HUB</span></div>'
    )