"""
Team Performance Page - Full Original Version
7 Tabs: Team Hours, Heatmap, Employees, Task Types, Gaps, Pipeline, Executive Summary
"""

import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data.team_data import load_team_data
from config.themes import T
from config.constants import DAILY_TARGET_HOURS
from ui.components import (
    render_page_header,
    show_info_box,
    section_title,
    card_metric,
    chart_explanation,
)


def render_team():
    """Render the full Team Performance dashboard."""
    render_page_header(
        "Team Performance Dashboard",
        "Upload your tasks file and analyze team workload, delivery, and pipeline performance.",
        "📊"
    )

    uploaded = st.file_uploader("Upload Team Excel File", type=["xlsx", "xls"], key="team_upload")

    if uploaded is None:
        show_info_box(
            "Upload an Excel file that includes columns such as <b>Assigned To</b>, <b>Date</b>, "
            "<b>Duration (Hours)</b>, <b>Status</b>, <b>Task Type</b>, <b>Completed</b>, and <b>Created At</b>.",
            "info"
        )
        return

    # ══════════════════════════════════════════════════════════════════
    # LOAD DATA
    # ══════════════════════════════════════════════════════════════════
    df, daily, emp, team_daily, days_under, days_over, not_reviewed, late_df = load_team_data(
        io.BytesIO(uploaded.read())
    )

    total_emps = int(df["Assigned To"].nunique()) if "Assigned To" in df.columns else 0
    total_tasks = len(df)
    total_hours = float(df["Duration_Hours"].sum()) if "Duration_Hours" in df.columns else 0
    comp_rate = float((df["Completed"].astype(str).eq("Yes").mean() * 100)) if "Completed" in df.columns and len(df) else 0
    late_count = int(df["Late_Entry"].sum()) if "Late_Entry" in df.columns else 0

    # ══════════════════════════════════════════════════════════════════
    # KPI CARDS - Row 1
    # ══════════════════════════════════════════════════════════════════
    m1, m2, m3, m4 = st.columns(4)
    card_metric(m1, total_emps, "Employees", T["accent"], "👥")
    card_metric(m2, total_tasks, "Total Tasks", T["accent2"], "📋")
    card_metric(m3, f"{total_hours:.0f}h", "Total Hours", T["green"], "⏱️")
    card_metric(m4, f"{comp_rate:.0f}%", "Completion Rate", T["amber"], "✅")

    # ══════════════════════════════════════════════════════════════════
    # KPI CARDS - Row 2
    # ══════════════════════════════════════════════════════════════════
    m5, m6, m7, m8 = st.columns(4)
    card_metric(m5, late_count, "Gap Tasks", T["red"], "⚠️")
    card_metric(m6, days_under, "Days < 8h", T["red"], "🔴")
    card_metric(m7, days_over, "Days > 8h", T["amber"], "🟡")
    card_metric(m8, not_reviewed, "Pending Review", T["muted"], "⏳")

    # ══════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════
    tabs = st.tabs([
        "📅 Team Hours",
        "🗺️ Heatmap",
        "👤 Employees",
        "📂 Task Types",
        "⚠️ Gaps",
        "🔄 Pipeline",
        "📋 Executive Summary",
    ])

    # ══════════════════════════════════════════════════════════════════
    # TAB 1: Team Hours
    # ══════════════════════════════════════════════════════════════════
    with tabs[0]:
        st.markdown('<div class="section-title">📅 Team Daily Hours</div>', unsafe_allow_html=True)

        fig1 = px.bar(
            team_daily,
            x='Date',
            y='Team_Hours',
            title='',
            labels={'Team_Hours': 'Hours', 'Date': 'Date'},
            color='Team_Hours',
            color_continuous_scale=['#BFDBFE', '#4F46E5'],
            text='Team_Hours'
        )
        fig1.update_traces(texttemplate='%{text:.0f}h', textposition='outside')
        fig1.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font_family='Cairo',
            height=420,
            margin=dict(t=20, b=40)
        )
        st.plotly_chart(fig1, use_container_width=True)

        chart_explanation(
            "What this chart shows:",
            "This bar chart represents the total number of working hours completed by the entire team "
            "for each day. It helps identify productivity trends, peak workload days, and days with "
            "lower team output."
        )

        st.markdown("**Table: Team Daily Hours**")
        st.dataframe(
            team_daily.assign(
                Date=team_daily['Date'].dt.strftime('%Y-%m-%d'),
                Team_Hours=team_daily['Team_Hours'].round(1)
            ).sort_values('Date'),
            use_container_width=True,
            hide_index=True
        )

    # ══════════════════════════════════════════════════════════════════
    # TAB 2: Heatmap
    # ══════════════════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown('<div class="section-title">🗺️ Heatmap: Employee Daily Hours</div>', unsafe_allow_html=True)
        st.caption("Dark = High hours · Light = Low hours")

        pivot = daily.pivot(index='Assigned To', columns='Date', values='Total_Hours').fillna(0)
        pivot.columns = [c.strftime('%m/%d') for c in pivot.columns]

        fig2 = px.imshow(
            pivot,
            labels=dict(x='Date', y='Employee', color='Hours'),
            color_continuous_scale='Blues',
            aspect='auto',
            text_auto='.1f'
        )
        fig2.update_layout(
            height=max(400, len(pivot) * 45 + 100),
            font_family='Cairo',
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=20)
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        <div class="chart-explanation">
        <strong>What this chart shows:</strong><br>
        This heatmap displays how many hours each employee worked per day.
        Darker colors indicate higher working hours, while lighter colors indicate lower hours.
        It helps quickly identify workload distribution and daily activity patterns across the team.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Table: Daily Hours with Status**")
        st.dataframe(
            daily.assign(
                Date=daily['Date'].dt.strftime('%Y-%m-%d'),
                Total_Hours=daily['Total_Hours'].round(2)
            ).sort_values(['Date', 'Total_Hours'], ascending=[True, False]),
            use_container_width=True,
            hide_index=True
        )

    # ══════════════════════════════════════════════════════════════════
    # TAB 3: Employees
    # ══════════════════════════════════════════════════════════════════
    with tabs[2]:
        st.markdown('<div class="section-title">👤 Employee Performance Overview</div>', unsafe_allow_html=True)

        if not emp.empty:
            top_emp = emp.sort_values('Total_Hours', ascending=False).copy()
            top_emp['Short_Name'] = top_emp['Assigned To'].apply(lambda x: ' '.join(str(x).split()[:2]))

            fig3 = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=['Total Hours by Employee', 'Completion Rate by Employee']
            )

            fig3.add_trace(go.Bar(
                x=top_emp['Short_Name'],
                y=top_emp['Total_Hours'],
                marker_color='#4F46E5',
                text=top_emp['Total_Hours'].round(1),
                textposition='outside'
            ), row=1, col=1)

            fig3.add_trace(go.Bar(
                x=top_emp['Short_Name'],
                y=top_emp['Completion_Rate_%'],
                marker_color='#16A34A',
                text=top_emp['Completion_Rate_%'].round(1).astype(str) + '%',
                textposition='outside'
            ), row=1, col=2)

            fig3.update_layout(
                height=450,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Cairo',
                margin=dict(t=40, b=50)
            )
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown("""
            <div class="chart-explanation">
            <strong>What this chart shows:</strong><br>
            The first chart compares total logged hours by employee.
            The second chart compares task completion rate across employees.
            Together they give a clear view of workload and execution quality.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Table: Employee Performance Details**")
            st.dataframe(
                emp.sort_values(['Total_Hours', 'Completion_Rate_%'], ascending=[False, False]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No employee summary available.")

    # ══════════════════════════════════════════════════════════════════
    # TAB 4: Task Types
    # ══════════════════════════════════════════════════════════════════
    with tabs[3]:
        st.markdown('<div class="section-title">📂 Task Type Distribution</div>', unsafe_allow_html=True)

        if 'Task Type' in df.columns:
            type_hours = (
                df.groupby('Task Type', dropna=False)['Duration_Hours']
                .sum()
                .reset_index()
                .sort_values('Duration_Hours', ascending=False)
            )

            fig4 = make_subplots(
                rows=1, cols=2,
                specs=[[{'type': 'domain'}, {'type': 'xy'}]],
                subplot_titles=['Task Type Share', 'Hours by Task Type']
            )

            fig4.add_trace(go.Pie(
                labels=type_hours['Task Type'],
                values=type_hours['Duration_Hours'].round(1),
                hole=0.4,
                textinfo='label+percent'
            ), row=1, col=1)

            fig4.add_trace(go.Bar(
                x=type_hours['Duration_Hours'].round(1),
                y=type_hours['Task Type'],
                orientation='h',
                marker_color='#4F46E5',
                text=type_hours['Duration_Hours'].round(1).astype(str) + 'h',
                textposition='outside'
            ), row=1, col=2)

            fig4.update_layout(
                height=480,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Cairo',
                showlegend=False,
                margin=dict(t=40)
            )
            st.plotly_chart(fig4, use_container_width=True)

            st.markdown("""
            <div class="chart-explanation">
            <strong>What this chart shows:</strong><br>
            The pie chart shows the percentage of total working hours spent on each task type.
            The bar chart shows the total number of hours spent per task type.
            Together, they help explain where the team's time is being invested.
            </div>
            """, unsafe_allow_html=True)

            type_table = df.groupby('Task Type').agg(
                Count=('ID', 'count'),
                Total_Hours=('Duration_Hours', 'sum'),
                Avg_Hours=('Duration_Hours', 'mean')
            ).round(2).reset_index().sort_values('Total_Hours', ascending=False)

            st.markdown("**Table: Task Type Breakdown**")
            st.dataframe(type_table, use_container_width=True, hide_index=True)
        else:
            st.warning("Column 'Task Type' not found.")

    # ══════════════════════════════════════════════════════════════════
    # TAB 5: Gaps
    # ══════════════════════════════════════════════════════════════════
    with tabs[4]:
        st.markdown(
            f'<div class="section-title">⚠️ Gap Entries Analysis — Total: {len(late_df)} Tasks</div>',
            unsafe_allow_html=True
        )
        st.caption("Late = task entered more than 24 hours after execution")

        if len(late_df) > 0:
            late_df2 = late_df.copy()
            late_df2['Entry_Delay_Hours'] = late_df2['Entry_Delay_Hours'].round(1)
            late_df2['Delay_Category'] = pd.cut(
                late_df2['Entry_Delay_Hours'],
                bins=[24, 48, 72, float('inf')],
                labels=['24-48h', '48-72h', '>72h']
            )

            late_by_emp = late_df2.groupby('Assigned To').size().reset_index(name='Late_Count')
            late_by_emp['Short_Name'] = late_by_emp['Assigned To'].apply(lambda x: ' '.join(str(x).split()[:2]))
            late_by_emp = late_by_emp.sort_values('Late_Count', ascending=True)

            delay_dist = late_df2['Delay_Category'].value_counts().reset_index()
            delay_dist.columns = ['Category', 'Count']
            delay_dist = delay_dist.sort_values('Category')

            fig5 = make_subplots(
                rows=1,
                cols=2,
                subplot_titles=['Late Entries per Employee', 'Delay Distribution']
            )

            fig5.add_trace(go.Bar(
                x=late_by_emp['Late_Count'],
                y=late_by_emp['Short_Name'],
                orientation='h',
                marker_color='#DC2626',
                text=late_by_emp['Late_Count'],
                textposition='outside'
            ), row=1, col=1)

            fig5.add_trace(go.Bar(
                x=delay_dist['Category'],
                y=delay_dist['Count'],
                marker_color='#D97706',
                text=delay_dist['Count'],
                textposition='outside'
            ), row=1, col=2)

            fig5.update_layout(
                height=430,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Cairo',
                margin=dict(t=40)
            )
            st.plotly_chart(fig5, use_container_width=True)

            st.markdown("""
            <div class="chart-explanation">
            <strong>What this chart shows:</strong><br>
            This analysis highlights delayed task entries.
            The first chart shows which employees submit the most late tasks,
            while the second shows how severe those delays are.
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**Table: Late Entries Details**")
            st.dataframe(
                late_df2[['Assigned To', 'Date', 'Task Type', 'Entry_Delay_Hours', 'Delay_Category']].sort_values(
                    'Entry_Delay_Hours', ascending=False
                ),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("No gap tasks detected.")

    # ══════════════════════════════════════════════════════════════════
    # TAB 6: Pipeline
    # ══════════════════════════════════════════════════════════════════
    with tabs[5]:
        st.markdown('<div class="section-title">🔄 Task Status Pipeline</div>', unsafe_allow_html=True)

        if 'Status' in df.columns:
            status_colors_map = {
                'Accepted': '#16A34A',
                'Not Reviewed': '#6B7280',
                'Rejected': '#DC2626',
                'Conflict': '#D97706',
                'Wait Kpi': '#7C3AED',
                'Not Completed': '#374151',
            }

            status_counts = df['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']

            has_review = 'Technical Review' in df.columns and 'KPI Review' in df.columns

            fig6 = make_subplots(
                rows=1,
                cols=2 if has_review else 1,
                specs=[[{'type': 'bar'}, {'type': 'bar'}]] if has_review else [[{'type': 'bar'}]],
                subplot_titles=['Status Distribution', 'Technical vs KPI Review'] if has_review else ['Status Distribution']
            )

            fig6.add_trace(go.Bar(
                x=status_counts['Status'],
                y=status_counts['Count'],
                marker_color=[status_colors_map.get(s, '#6B7280') for s in status_counts['Status']],
                text=status_counts['Count'],
                textposition='outside'
            ), row=1, col=1)

            if has_review:
                review_data = pd.DataFrame({
                    'Type': ['Technical Review', 'Technical Review', 'KPI Review', 'KPI Review'],
                    'Status': ['Reviewed', 'Not Reviewed', 'Reviewed', 'Not Reviewed'],
                    'Count': [
                        (df['Technical Review'] == 'Reviewed').sum(),
                        (df['Technical Review'] == 'Not Reviewed').sum(),
                        (df['KPI Review'] == 'Reviewed').sum(),
                        (df['KPI Review'] == 'Not Reviewed').sum(),
                    ]
                })

                for status, color in [('Reviewed', '#16A34A'), ('Not Reviewed', '#DC2626')]:
                    d = review_data[review_data['Status'] == status]
                    fig6.add_trace(go.Bar(
                        name=status,
                        x=d['Type'],
                        y=d['Count'],
                        marker_color=color,
                        text=d['Count'],
                        textposition='outside'
                    ), row=1, col=2)

            fig6.update_layout(
                height=420,
                barmode='group',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font_family='Cairo',
                margin=dict(t=40)
            )
            st.plotly_chart(fig6, use_container_width=True)

            st.markdown("""
            <div class="chart-explanation">
            <strong>What this chart shows:</strong><br>
            This chart shows how tasks are distributed across their current workflow statuses
            such as Accepted, Rejected, or Not Reviewed.
            If review columns are available, it also compares Technical Review and KPI Review progress.
            It helps highlight workflow bottlenecks and pending review stages.
            </div>
            """, unsafe_allow_html=True)

            if has_review:
                not_rev_df = df[(df['Technical Review'] == 'Not Reviewed') & (df['KPI Review'] == 'Not Reviewed')]
                if len(not_rev_df) > 0:
                    st.markdown("**Table: Pending in Both Technical and KPI Review**")
                    st.dataframe(not_rev_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Column 'Status' not found.")

    # ══════════════════════════════════════════════════════════════════
    # TAB 7: Executive Summary
    # ══════════════════════════════════════════════════════════════════
    with tabs[6]:
        section_title("📋 Executive Summary")

        # ── values ──
        top_emp_hours = (
            emp.sort_values("Total_Hours", ascending=False).iloc[0]["Assigned To"]
            if len(emp) > 0 else "—"
        )
        top_emp_late = (
            emp.sort_values("Late_Entries", ascending=False).iloc[0]["Assigned To"]
            if len(emp) > 0 else "—"
        )

        pct_under = f"{int(days_under)} days ({days_under / max(len(daily), 1) * 100:.0f}%)"
        pct_over = f"{int(days_over)}  days ({days_over / max(len(daily), 1) * 100:.0f}%)"
        late_pct = (
            f"{int(df['Late_Entry'].sum())} tasks ({df['Late_Entry'].mean() * 100:.1f}%)"
            if "Late_Entry" in df.columns else "—"
        )
        wait_kpi = f"{int((df['Status'] == 'Wait Kpi').sum())} tasks" if "Status" in df.columns else "—"
        conflicts = f"{int((df['Status'] == 'Conflict').sum())} tasks" if "Status" in df.columns else "—"

        # ── rows ──
        left_rows = [
            ("👥 Employees", str(df["Assigned To"].nunique()) if "Assigned To" in df.columns else "—"),
            ("📋 Total Tasks", str(total_tasks)),
            ("⏱️ Total Hours", f"{total_hours:.1f}h"),
            ("✅ Completion Rate", f"{comp_rate:.1f}%"),
            (f"🔴 Days < {DAILY_TARGET_HOURS}h", pct_under),
            (f"🟡 Days > {DAILY_TARGET_HOURS}h", pct_over),
        ]
        right_rows = [
            ("⚠️ Gap Tasks", late_pct),
            ("⏳ Pending Tech + KPI", f"{int(not_reviewed)} tasks"),
            ("🔴 Wait KPI", wait_kpi),
            ("❗ Conflicts", conflicts),
            ("🏆 Top Employee (Hours)", top_emp_hours),
            ("⚠️ Most Gap Entries", top_emp_late),
        ]

        # ── HTML table renderer ──
        def _exec_table(rows):
            trows = ""
            for i, (lbl, val) in enumerate(rows):
                alt_bg = T["sum_bg_alt"] if i % 2 else T["sum_bg"]
                border = f'border-top:1px solid {T["sum_row_border"]};' if i > 0 else ""
                trows += (
                    f'<tr style="background:{alt_bg};">'
                    f'<td style="{border}padding:12px 18px;color:{T["sum_key_color"]};'
                    f'font-size:.88rem;font-family:DM Sans,sans-serif;">{lbl}</td>'
                    f'<td style="{border}padding:12px 18px;text-align:right;font-weight:700;'
                    f'color:{T["sum_val_color"]};font-size:.9rem;font-family:Syne,sans-serif;'
                    f'white-space:nowrap;">{val}</td>'
                    f'</tr>'
                )
            return (
                f'<div style="background:{T["sum_bg"]};border:1px solid {T["border"]};'
                f'border-radius:14px;overflow:hidden;">'
                f'<table style="width:100%;border-collapse:collapse;">'
                f'<tbody>{trows}</tbody></table></div>'
            )

        col_l, col_r = st.columns(2, gap="large")
        col_l.markdown(_exec_table(left_rows), unsafe_allow_html=True)
        col_r.markdown(_exec_table(right_rows), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        summary_df = pd.DataFrame(left_rows + right_rows, columns=["Metric", "Value"])
        csv = summary_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "⬇️ Download Summary as CSV",
            data=csv,
            file_name="executive_summary.csv",
            mime="text/csv",
        )