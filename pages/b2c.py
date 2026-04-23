"""
B2C Executive Review Page - Full Original Version
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from data.b2c_data import load_b2c_data
from config.themes import T
from config.constants import EVAL_AR_COLS
from ui.components import (
    render_page_header,
    show_info_box,
    section_title,
    kpi,
)


def render_b2c():
    """Render the full B2C Executive Review dashboard."""
    render_page_header(
        "Session Review Dashboard Executive",
        "Executive view for B2C session delivery, recommendation, and feedback quality.",
        "🔍"
    )

    uploaded = st.file_uploader("Upload B2C Review Excel File", type=["xlsx"], key="b2c_upload")

    if uploaded is None:
        show_info_box("Upload the B2C review file to activate the executive dashboard.", "info")
        return

    df_full = load_b2c_data(uploaded.getvalue())
    dff = df_full.copy()

    # ─────────────────────────────────────────────────────────────
    # Local theme mapping for this page
    # ─────────────────────────────────────────────────────────────
    CHART_H = 325
    PAPER = "rgba(0,0,0,0)"
    PLOT = T["surface"]
    GRID = T["border"]
    FONT = dict(family="Almarai", color=T["text"])
    TITLE_FONT = dict(family="Almarai", size=17, color=T["text"])

    ACCENT = {
        "wine": T["accent"],
        "wine_soft": T["accent2"],
        "gold": T["amber"],
        "gold_soft": T["border"],
        "ink": T["text"],
        "green": T["green"],
        "amber": T["amber"],
        "red": T["red"],
        "slate": T["muted"],
    }

    def fmt_num(v, d=1):
        if pd.isna(v):
            return "—"
        return f"{v:.{d}f}"

    def fmt_pct(v):
        if pd.isna(v):
            return "—"
        return f"{v:.1f}%"

    def pct_yes(series: pd.Series):
        valid = series.dropna()
        if len(valid) == 0:
            return np.nan
        return round((valid.astype(str) == "Yes").mean() * 100, 1)

    def insight(text: str, kind: str = ""):
        border = T["accent"]
        bg = T["surface"]
        fg = T["text"]
        if kind == "insight-good":
            border = T["green"]
            bg = "#F0FDF4" if st.session_state.theme == "light" else "rgba(16,185,129,.10)"
            fg = T["green"] if st.session_state.theme == "light" else "#A7F3D0"
        elif kind == "insight-warn":
            border = T["amber"]
            bg = "#FFFBEB" if st.session_state.theme == "light" else "rgba(245,158,11,.10)"
            fg = T["amber"] if st.session_state.theme == "light" else "#FDE68A"

        st.markdown(
            f"""
            <div style="
                background:{bg};
                border-left:4px solid {border};
                border:1px solid {T['border']};
                border-left-width:4px;
                border-radius:0 12px 12px 0;
                padding:.85rem 1rem;
                font-size:.86rem;
                color:{fg};
                line-height:1.7;
                margin:.55rem 0 1rem;
            ">
                💡 {text}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ══════════════════════════════════════════════════════════════════
    # CALCULATE KPIs
    # ══════════════════════════════════════════════════════════════════
    n = len(dff)
    avg_eval = (
        round(dff["Instructor Evaluation"].mean(), 2)
        if "Instructor Evaluation" in dff.columns and dff["Instructor Evaluation"].notna().any()
        else np.nan
    )
    avg_interaction = (
        round(dff["Student Interaction Rate"].mean(), 2)
        if "Student Interaction Rate" in dff.columns and dff["Student Interaction Rate"].notna().any()
        else np.nan
    )
    on_time_pct = pct_yes(dff["On Time"]) if "On Time" in dff.columns else np.nan
    practical_pct = pct_yes(dff["Practical Exercise"]) if "Practical Exercise" in dff.columns else np.nan
    recommend_pct = pct_yes(dff["Recommend Continuation"]) if "Recommend Continuation" in dff.columns else np.nan
    understood_pct = pct_yes(dff["Students Understood"]) if "Students Understood" in dff.columns else np.nan
    avg_attendance = (
        round(dff["Attendance"].mean(), 1)
        if "Attendance" in dff.columns and dff["Attendance"].notna().any()
        else np.nan
    )

    if "Feedback Sentiment Score" in dff.columns:
        avg_sent_score = (
            round(dff["Feedback Sentiment Score"].mean(), 1)
            if dff["Feedback Sentiment Score"].notna().any()
            else np.nan
        )
    elif "Feedback Score" in dff.columns:
        avg_sent_score = (
            round(dff["Feedback Score"].mean(), 1)
            if dff["Feedback Score"].notna().any()
            else np.nan
        )
        dff["Feedback Sentiment Score"] = dff["Feedback Score"]
    else:
        avg_sent_score = np.nan

    # ══════════════════════════════════════════════════════════════════
    # KPI CARDS - Row 1
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">📌 Executive KPIs</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    kpi(k1, "🗂️", n, "Total Reviews", "Filtered records under current controls", "ink")
    kpi(k2, "⭐", fmt_num(avg_eval, 2), "Avg Instructor Score", "Composite score across teaching dimensions", "gold")
    kpi(k3, "🙋", fmt_num(avg_interaction, 2), "Avg Student Interaction", "Reported interaction intensity", "wine")
    kpi(k4, "⏱️", fmt_pct(on_time_pct), "On-Time Sessions", "Delivery discipline and timing adherence", "green" if pd.notna(on_time_pct) and on_time_pct >= 70 else "amber")
    kpi(k5, "🧪", fmt_pct(practical_pct), "Practical Exercise", "Hands-on learning presence", "amber")
    kpi(k6, "👍", fmt_pct(recommend_pct), "Recommend Continuation", "Would reviewers keep instructor with same group?", "green" if pd.notna(recommend_pct) and recommend_pct >= 70 else "red")

    # ══════════════════════════════════════════════════════════════════
    # KPI CARDS - Row 2
    # ══════════════════════════════════════════════════════════════════
    r1, r2, r3 = st.columns(3)
    kpi(r1, "👥", fmt_num(avg_attendance, 1), "Avg Attendance", "Estimated students per session", "wine")
    kpi(r2, "🧠", fmt_pct(understood_pct), "Students Understood", "Reviewer-based learner understanding signal", "green")
    kpi(r3, "💬", fmt_num(avg_sent_score, 1), "Feedback Tone Score", "Open comments pulse on a 100-point scale", "gold")

    # ══════════════════════════════════════════════════════════════════
    # QUALITY OVERVIEW
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🧭 Quality Overview</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, 1])

    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        available_eval_cols = [col for col in EVAL_AR_COLS if col in dff.columns]
        if available_eval_cols:
            quality_means = dff[available_eval_cols].mean().round(2).reset_index()
            quality_means.columns = ["Metric", "Score"]
            fig = px.bar(
                quality_means,
                x="Score",
                y="Metric",
                orientation="h",
                text="Score",
                color="Score",
                color_continuous_scale=[
                    [0, "#f2dfc6"],
                    [0.5, "#d7b46d"],
                    [1, "#7f132d"],
                ],
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(
                title=dict(text="Average Quality by Evaluation Dimension", font=TITLE_FONT),
                height=CHART_H + 40,
                coloraxis_showscale=False,
                paper_bgcolor=PAPER,
                plot_bgcolor=PLOT,
                font=FONT,
                margin=dict(t=55, b=20, l=10, r=20),
                yaxis=dict(autorange="reversed"),
                xaxis_title="Average Score",
                yaxis_title="",
            )
            fig.update_xaxes(showgrid=True, gridcolor=GRID)
            fig.update_yaxes(showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if available_eval_cols:
            strongest = dff[available_eval_cols].mean().idxmax()
            weakest = dff[available_eval_cols].mean().idxmin()
            insight(
                f"<b>Strongest dimension:</b> {strongest}<br>"
                f"<b>Needs attention:</b> {weakest}<br>"
                f"This panel makes the quality balance visible across explanation clarity, structure, "
                f"learner response, and practical relevance.",
                "insight-good"
            )

    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        donut_df = pd.DataFrame(
            {
                "Metric": ["On Time", "Practical Exercise", "Recommendation", "Students Understood"],
                "Value": [on_time_pct, practical_pct, recommend_pct, understood_pct],
            }
        ).dropna()
        if not donut_df.empty:
            fig2 = px.bar(
                donut_df,
                x="Metric",
                y="Value",
                text="Value",
                color="Value",
                color_continuous_scale=[[0, "#f4e8d8"], [0.55, "#d6b56b"], [1, "#7f132d"]],
            )
            fig2.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig2.update_layout(
                title=dict(text="Operational Success Metrics", font=TITLE_FONT),
                height=CHART_H + 40,
                coloraxis_showscale=False,
                paper_bgcolor=PAPER,
                plot_bgcolor=PLOT,
                font=FONT,
                margin=dict(t=55, b=30, l=10, r=10),
                yaxis_title="Percentage",
                xaxis_title="",
            )
            fig2.update_yaxes(showgrid=True, gridcolor=GRID, range=[0, 100])
            fig2.update_xaxes(showgrid=False)
            st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        insight(
            "This block reflects delivery maturity: timing discipline, use of hands-on exercises, "
            "perceived learner understanding, and instructor continuity confidence."
        )

    # ══════════════════════════════════════════════════════════════════
    # INSTRUCTOR ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">👨‍🏫 Instructor Analysis</div>', unsafe_allow_html=True)
    c3, c4 = st.columns([1.28, 1])

    with c3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if "Instructor" in dff.columns:
            instructor_scorecard = dff.groupby("Instructor").agg(
                Reviews=("Instructor", "count"),
                Avg_Eval=("Instructor Evaluation", "mean"),
                Avg_Interaction=("Student Interaction Rate", "mean"),
                Avg_Attendance=("Attendance", "mean"),
                On_Time_Pct=("On Time", lambda x: pct_yes(x)),
                Practical_Pct=("Practical Exercise", lambda x: pct_yes(x)),
                Recommend_Pct=("Recommend Continuation", lambda x: pct_yes(x)),
            ).reset_index().sort_values(["Avg_Eval", "Recommend_Pct"], ascending=False)

            display_df = instructor_scorecard.copy()
            for col in ["Avg_Eval", "Avg_Interaction", "Avg_Attendance", "On_Time_Pct", "Practical_Pct", "Recommend_Pct"]:
                display_df[col] = display_df[col].round(2)
            st.markdown("**Instructor Scorecard**")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if "Instructor" in dff.columns and "Instructor Evaluation" in dff.columns:
            best_df = (
                dff.groupby("Instructor", as_index=False)["Instructor Evaluation"]
                .mean()
                .sort_values("Instructor Evaluation", ascending=False)
            )
            fig3 = px.bar(
                best_df,
                x="Instructor",
                y="Instructor Evaluation",
                text="Instructor Evaluation",
                color="Instructor Evaluation",
                color_continuous_scale=[[0, "#ead7a1"], [0.5, "#c7a14a"], [1, "#7f132d"]],
            )
            fig3.update_traces(texttemplate="%{y:.2f}", textposition="outside")
            fig3.update_layout(
                title=dict(text="Average Instructor Evaluation", font=TITLE_FONT),
                height=CHART_H + 35,
                coloraxis_showscale=False,
                paper_bgcolor=PAPER,
                plot_bgcolor=PLOT,
                font=FONT,
                margin=dict(t=55, b=55, l=10, r=10),
                xaxis_title="",
                yaxis_title="Average Score",
            )
            fig3.update_yaxes(showgrid=True, gridcolor=GRID)
            fig3.update_xaxes(showgrid=False)
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        insight(
            "Use the scorecard for precision and the bar chart for visual ranking. "
            "Together they show who is strongest, who is stable, and who needs targeted coaching.",
            "insight-good"
        )

    # ══════════════════════════════════════════════════════════════════
    # ENGAGEMENT & CORRELATIONS
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🔗 Engagement & Correlations</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)

    with c5:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if {"Instructor Evaluation", "Student Interaction Rate"}.issubset(dff.columns):
            sc_df = dff.dropna(subset=["Instructor Evaluation", "Student Interaction Rate"]).copy()

            if "Attendance" in sc_df.columns:
                sc_df["Attendance"] = pd.to_numeric(sc_df["Attendance"], errors="coerce")
                sc_df["Attendance"] = sc_df["Attendance"].fillna(1)
                sc_df.loc[sc_df["Attendance"] <= 0, "Attendance"] = 1

            if not sc_df.empty:
                color_col = "Recommend Continuation" if "Recommend Continuation" in sc_df.columns else None

                fig4 = px.scatter(
                    sc_df,
                    x="Instructor Evaluation",
                    y="Student Interaction Rate",
                    color=color_col,
                    color_discrete_map={"Yes": ACCENT["green"], "No": ACCENT["red"]},
                    size="Attendance" if "Attendance" in sc_df.columns else None,
                    hover_data=[c for c in ["Instructor", "Group", "On Time"] if c in sc_df.columns],
                    opacity=0.82,
                )
                if len(sc_df) >= 2:
                    x = sc_df["Instructor Evaluation"].to_numpy(dtype=float)
                    y = sc_df["Student Interaction Rate"].to_numpy(dtype=float)
                    if len(np.unique(x)) > 1:
                        slope, intercept = np.polyfit(x, y, 1)
                        x_line = np.linspace(x.min(), x.max(), 100)
                        y_line = slope * x_line + intercept
                        fig4.add_trace(
                            go.Scatter(
                                x=x_line, y=y_line, mode="lines", name="Trend",
                                line=dict(width=2.4, dash="dash", color=ACCENT["wine"])
                            )
                        )
                fig4.update_layout(
                    title=dict(text="Evaluation vs Student Interaction", font=TITLE_FONT),
                    height=CHART_H + 20,
                    paper_bgcolor=PAPER,
                    plot_bgcolor=PLOT,
                    font=FONT,
                    margin=dict(t=55, b=30, l=10, r=10),
                )
                fig4.update_xaxes(showgrid=True, gridcolor=GRID)
                fig4.update_yaxes(showgrid=True, gridcolor=GRID)
                st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if {"Instructor Evaluation", "Student Interaction Rate"}.issubset(dff.columns):
            corr_df = dff[["Instructor Evaluation", "Student Interaction Rate"]].dropna()
            corr = corr_df.corr().iloc[0, 1] if len(corr_df) > 1 else np.nan
            insight(
                f"<b>Correlation coefficient:</b> {fmt_num(corr, 2)}<br>"
                f"A stronger positive value means sessions that are rated highly also tend to "
                f"stimulate more learner interaction."
            )

    with c6:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if {"Group", "Student Interaction Rate"}.issubset(dff.columns):
            fig5 = px.box(
                dff.dropna(subset=["Group", "Student Interaction Rate"]),
                x="Group",
                y="Student Interaction Rate",
                color="Group",
                points="all",
                color_discrete_sequence=["#7f132d", "#c7a14a", "#1d1718", "#b8647a", "#d6b56b"],
            )
            fig5.update_layout(
                title=dict(text="Interaction Distribution by Group", font=TITLE_FONT),
                height=CHART_H + 20,
                showlegend=False,
                paper_bgcolor=PAPER,
                plot_bgcolor=PLOT,
                font=FONT,
                margin=dict(t=55, b=40, l=10, r=10),
                xaxis_title="Group",
                yaxis_title="Interaction Rate",
            )
            fig5.update_yaxes(showgrid=True, gridcolor=GRID)
            fig5.update_xaxes(showgrid=False)
            st.plotly_chart(fig5, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        insight(
            "Box plots show stability, not just averages. A compact high box means a consistently "
            "strong experience, while a wide spread means learners are not receiving the same "
            "session quality every time."
        )

    # ══════════════════════════════════════════════════════════════════
    # RECOMMENDATION & DELIVERY
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🛠️ Recommendation & Delivery</div>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)

    with c7:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if "Instructor" in dff.columns and "Recommend Continuation" in dff.columns:
            rec_df = dff.groupby("Instructor", as_index=False).agg(
                Recommend_Pct=("Recommend Continuation", lambda x: pct_yes(x))
            )
            fig6 = px.bar(
                rec_df.sort_values("Recommend_Pct", ascending=False),
                x="Instructor",
                y="Recommend_Pct",
                text="Recommend_Pct",
                color="Recommend_Pct",
                color_continuous_scale=[[0, "#f4e8d8"], [0.55, "#d6b56b"], [1, "#7f132d"]],
            )
            fig6.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig6.update_layout(
                title=dict(text="Recommendation Rate by Instructor", font=TITLE_FONT),
                height=CHART_H + 20,
                coloraxis_showscale=False,
                paper_bgcolor=PAPER,
                plot_bgcolor=PLOT,
                font=FONT,
                margin=dict(t=55, b=50, l=10, r=10),
                yaxis_title="Recommendation %",
                xaxis_title="",
            )
            fig6.update_yaxes(showgrid=True, gridcolor=GRID, range=[0, 100])
            fig6.update_xaxes(showgrid=False)
            st.plotly_chart(fig6, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c8:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if "Practical Exercise" in dff.columns and "Students Participated" in dff.columns:
            practical_counts = pd.DataFrame({
                "Metric": ["Practical Exercise", "Students Participated"],
                "Percentage": [pct_yes(dff["Practical Exercise"]), pct_yes(dff["Students Participated"])],
            }).dropna()
            fig7 = px.bar(
                practical_counts,
                x="Metric",
                y="Percentage",
                text="Percentage",
                color="Metric",
                color_discrete_sequence=[ACCENT["gold"], ACCENT["wine"]],
            )
            fig7.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
            fig7.update_layout(
                title=dict(text="Hands-On Delivery vs Participation", font=TITLE_FONT),
                height=CHART_H + 20,
                showlegend=False,
                paper_bgcolor=PAPER,
                plot_bgcolor=PLOT,
                font=FONT,
                margin=dict(t=55, b=30, l=10, r=10),
                yaxis_title="Percentage",
                xaxis_title="",
            )
            fig7.update_yaxes(showgrid=True, gridcolor=GRID, range=[0, 100])
            fig7.update_xaxes(showgrid=False)
            st.plotly_chart(fig7, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        insight(
            "This section connects classroom mechanics with reviewer trust: whether practice was "
            "present, whether students actually joined the solution process, and whether that "
            "translated into keeping the same instructor."
        )

    # ══════════════════════════════════════════════════════════════════
    # TIMELINE
    # ══════════════════════════════════════════════════════════════════
    if "Session Date" in dff.columns and dff["Session Date"].notna().any():
        st.markdown('<div class="section-title">📅 Timeline</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        time_df = dff.dropna(subset=["Session Date"]).copy()
        time_df["Week"] = time_df["Session Date"].dt.to_period("W").apply(lambda r: r.start_time)
        weekly = time_df.groupby("Week").agg(
            Reviews=("Week", "count"),
            Avg_Eval=("Instructor Evaluation", "mean"),
            Avg_Interaction=("Student Interaction Rate", "mean"),
        ).reset_index()

        fig8 = go.Figure()
        fig8.add_trace(
            go.Scatter(
                x=weekly["Week"], y=weekly["Reviews"], mode="lines+markers", name="Reviews",
                line=dict(width=2.8, color=ACCENT["wine"]),
                fill="tozeroy", fillcolor="rgba(127,19,45,.08)"
            )
        )
        if "Avg_Eval" in weekly.columns:
            fig8.add_trace(
                go.Scatter(
                    x=weekly["Week"], y=weekly["Avg_Eval"], mode="lines+markers", name="Avg Eval",
                    line=dict(width=2.1, dash="dash", color=ACCENT["gold"]), yaxis="y2"
                )
            )
        if "Avg_Interaction" in weekly.columns:
            fig8.add_trace(
                go.Scatter(
                    x=weekly["Week"], y=weekly["Avg_Interaction"], mode="lines+markers",
                    name="Avg Interaction",
                    line=dict(width=2.1, dash="dot", color=ACCENT["green"]), yaxis="y2"
                )
            )
        fig8.update_layout(
            title=dict(text="Weekly Trend of Reviews, Evaluation, and Interaction", font=TITLE_FONT),
            height=CHART_H,
            paper_bgcolor=PAPER,
            plot_bgcolor=PLOT,
            font=FONT,
            margin=dict(t=55, b=30, l=10, r=55),
            hovermode="x unified",
            yaxis=dict(title="Review Count", showgrid=True, gridcolor=GRID),
            yaxis2=dict(title="Average Score", overlaying="y", side="right", showgrid=False),
        )
        fig8.update_xaxes(showgrid=False)
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        insight(
            "Use the timeline to see whether increased review volume coincides with stronger "
            "delivery quality or whether scale is starting to erode engagement."
        )

    # ══════════════════════════════════════════════════════════════════
    # FEEDBACK & NOTES
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">💬 Feedback & Notes</div>', unsafe_allow_html=True)
    f1, f2 = st.columns([1.16, 1])

    with f1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        feedback_cols = [c for c in ["Open Feedback", "Reason"] if c in dff.columns]
        if feedback_cols:
            cards_df = dff.copy()
            cards_df["Combined Notes"] = ""
            for c in feedback_cols:
                cards_df["Combined Notes"] = (
                    cards_df["Combined Notes"].fillna("") + cards_df[c].fillna("").astype(str) + " "
                )
            cards_df["Combined Notes"] = cards_df["Combined Notes"].str.strip()
            cards_df = cards_df[cards_df["Combined Notes"] != ""]

            st.markdown(f"**Review Notes** — {len(cards_df)} entries")
            if len(cards_df) == 0:
                st.info("No text feedback under current filters.")
            else:
                show_count = min(20, len(cards_df))
                for _, row in cards_df.head(show_count).iterrows():
                    sent = row.get("Feedback Sentiment", "Neutral")
                    score = row.get("Feedback Sentiment Score", 50)
                    border = (
                        ACCENT["green"] if sent == "Positive"
                        else ACCENT["red"] if sent == "Negative"
                        else ACCENT["gold"]
                    )
                    badge_bg = (
                        "#eefbf2" if sent == "Positive"
                        else "#fff1f1" if sent == "Negative"
                        else "#fff8eb"
                    )
                    badge_tx = border
                    st.markdown(
                        f"""
                        <div style="border:1px solid rgba(199,161,74,.16);border-left:5px solid {border};
                                    border-radius:16px;padding:1rem 1.05rem;margin-bottom:.78rem;
                                    background:linear-gradient(180deg,#fffdfa,#fff7ed);
                                    box-shadow:0 8px 18px rgba(73,41,18,.04);">
                            <div style="display:flex;justify-content:space-between;gap:1rem;
                                        align-items:center;margin-bottom:.42rem;flex-wrap:wrap;">
                                <div style="font-size:.8rem;color:#7c6860;">
                                    {row.get('Instructor', '—')} · {row.get('Group', '—')}
                                </div>
                                <div style="background:{badge_bg};color:{badge_tx};
                                            border:1px solid {border}33;border-radius:999px;
                                            padding:.22rem .72rem;font-size:.76rem;font-weight:600;">
                                    {sent} ({score})
                                </div>
                            </div>
                            <div style="font-size:.93rem;color:#201615;line-height:1.65;">
                                {row['Combined Notes']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                if len(cards_df) > show_count:
                    st.caption(f"Showing first {show_count} notes out of {len(cards_df)}.")
        st.markdown('</div>', unsafe_allow_html=True)

    with f2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        if "Feedback Sentiment" in dff.columns:
            sent_counts = dff["Feedback Sentiment"].value_counts().reset_index()
            sent_counts.columns = ["Sentiment", "Count"]
            fig9 = px.pie(
                sent_counts,
                names="Sentiment",
                values="Count",
                hole=0.6,
                color="Sentiment",
                color_discrete_map={
                    "Positive": ACCENT["green"],
                    "Neutral": ACCENT["gold"],
                    "Negative": ACCENT["red"],
                },
            )
            fig9.update_layout(
                title=dict(text="Feedback Sentiment Distribution", font=TITLE_FONT),
                height=CHART_H - 25,
                showlegend=True,
                paper_bgcolor=PAPER,
                font=FONT,
                margin=dict(t=55, b=10, l=10, r=10),
            )
            st.plotly_chart(fig9, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        insight(
            "The comment cards preserve reviewer voice, while the sentiment ring gives a quick "
            "emotional reading across all open notes."
        )

    # ══════════════════════════════════════════════════════════════════
    # DETAILED RECORDS
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🗃️ Detailed Records</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    priority_cols = [
        "Session Date", "Instructor", "Group", "Session Mode", "Instructor Evaluation",
        "Attendance", "Student Interaction Rate", "On Time", "Students Understood",
        "Practical Exercise", "Students Participated", "Recommend Continuation",
        "Open Feedback", "Reason"
    ]
    show_cols = [c for c in priority_cols if c in dff.columns]
    st.dataframe(dff[show_cols], use_container_width=True, hide_index=True, height=360)

    csv_data = dff.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "⬇️ Download filtered CSV",
        data=csv_data,
        file_name="session_review_dashboard_executive_filtered.csv",
        mime="text/csv",
        use_container_width=False,
    )
    st.markdown('</div>', unsafe_allow_html=True)
    insight(
        "This table is the live source behind all visual metrics. "
        "Every filter on the left reshapes the full executive view immediately."
    )

    st.markdown('</div>', unsafe_allow_html=True)