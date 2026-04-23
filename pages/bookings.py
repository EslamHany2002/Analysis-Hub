"""
Bookings Attendance Page - Full Original Version
Automation pipeline + 12 KPIs + 12 Charts + 6 Tabs
"""

import os
import io
import time
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from data.bookings_data import load_bookings_excel, prepare_bookings
from config.themes import T
from ui.components import (
    render_page_header,
    show_info_box,
    plotly_layout,
)
from workers import run_automation_pipeline


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def clear_bookings_cache():
    """Clear cached bookings data."""
    st.cache_data.clear()


def load_final_automation_output():
    """Load the merged CSV from automation."""
    csv_path = "final_merged_analysis.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            if not df.empty:
                return df
        except Exception:
            pass
    return None


def vertical_kpi(value, label, color, icon):
    """Render a vertical KPI card (original bookings style)."""
    return f"""
    <div style="
        background:{T['surface']};
        border:1px solid {T['border']};
        border-bottom: 4px solid {color};
        border-radius:16px;
        padding: 20px 10px;
        text-align: center;
        height: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;">
        <div style="font-size: 2.2rem; margin-bottom: 8px;">{icon}</div>
        <div style="
            font-family: 'Almarai', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: {color};
            line-height: 1.1;
            margin-bottom: 6px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;">{value}</div>
        <div style="
            font-family: 'Kalam', cursive;
            font-size: 0.95rem;
            color: {T['muted']};
            line-height: 1.2;">{label}</div>
    </div>"""


def classify_hour(h):
    """Classify hour into day period."""
    if pd.isna(h):
        return "Unknown"
    h = int(h)
    if 6 <= h < 12:
        return "Morning"
    elif 12 <= h < 17:
        return "Afternoon"
    elif 17 <= h < 21:
        return "Evening"
    return "Off Hours"


# ══════════════════════════════════════════════════════════════════
# MAIN RENDER
# ══════════════════════════════════════════════════════════════════

def render_bookings():
    """Render the full Bookings Attendance dashboard."""
    render_page_header(
        "Bookings Attendance Dashboard",
        "Automated pipeline for monthly data, analysis, advanced insights, and visual storytelling.",
        "📅"
    )

    # ══════════════════════════════════════════════════════════════════
    # 1) Automation Area
    # ══════════════════════════════════════════════════════════════════
    st.markdown(
        '<div class="chart-card" style="text-align:center; padding: 20px; margin-bottom: 20px; border: 2px dashed #6366f1;">',
        unsafe_allow_html=True
    )
    st.markdown(f"""
    <div style="font-family:Kalam,cursive; font-size:1.2rem; color:{T['text']}; margin-bottom:10px;">
        🤖 Automation Pipeline
    </div>
    <div style="font-size:0.85rem; color:{T['muted']}; margin-bottom:15px;">
        Click to download Bookings, Teams Attendance, merge automatically, and refresh the dashboard.
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Run Full Automation", type="primary", use_container_width=True):
        with st.spinner("Running automation pipeline... Please wait"):
            result = run_automation_pipeline()

        if result["ok"]:
            clear_bookings_cache()
            st.success("✅ Pipeline completed successfully.")
            if result.get("stdout"):
                st.code(result["stdout"], language="text")
            time.sleep(2)
            st.rerun()
        else:
            st.error("❌ Pipeline failed.")
            if result.get("stderr"):
                st.code(result["stderr"], language="text")
            elif result.get("stdout"):
                st.code(result["stdout"], language="text")

    st.markdown("</div>", unsafe_allow_html=True)

    final_df = load_final_automation_output()
    if final_df is not None and not final_df.empty:
        st.markdown("### Automated Merged Output")
        st.dataframe(final_df, use_container_width=True)
    else:
        st.info("No merged output found yet. Run the automation first.")

    # ══════════════════════════════════════════════════════════════════
    # 2) Data Loading
    # ══════════════════════════════════════════════════════════════════
    df_source = None
    csv_path = "final_merged_analysis.csv"

    if os.path.exists(csv_path):
        st.info(f"📂 Displaying data from automated pipeline: `{csv_path}`")
        df_source = pd.read_csv(csv_path)

        df_source = df_source.rename(columns={
            "Booking DateTime": "Date Time",
        })

        if "Date Time" in df_source.columns:
            df_source["Date Time"] = pd.to_datetime(df_source["Date Time"], errors="coerce")
            df_source = df_source.dropna(subset=["Date Time"]).copy()
            df_source["Date"] = df_source["Date Time"].dt.date
            df_source["Month"] = df_source["Date Time"].dt.to_period("M").astype(str)
            df_source["Month Start"] = df_source["Date Time"].dt.to_period("M").dt.to_timestamp()
            df_source["Day Name"] = df_source["Date Time"].dt.day_name()
            df_source["Hour"] = df_source["Date Time"].dt.hour
            df_source["Time Slot"] = df_source["Date Time"].dt.strftime("%H:%M")
            df_source["Week"] = df_source["Date Time"].dt.isocalendar().week.astype(int)
            df_source["Year"] = df_source["Date Time"].dt.year
            df_source["Day Number"] = df_source["Date Time"].dt.day

    else:
        uploaded_file = st.file_uploader("Or upload merged Excel file", type=["xlsx"], key="bookings_upload")
        if uploaded_file:
            try:
                sheets = load_bookings_excel(uploaded_file)
                if "Bookings_Updated" in sheets:
                    df_source = prepare_bookings(sheets["Bookings_Updated"])
            except Exception as e:
                st.error(f"Error reading file: {e}")

    if df_source is None or df_source.empty:
        show_info_box("Click the button above to run automation, or upload a file manually.", "info")
        return

    # ══════════════════════════════════════════════════════════════════
    # 3) Data Cleanup / Standardization
    # ══════════════════════════════════════════════════════════════════
    if "Status" in df_source.columns:
        df_source["Status"] = df_source["Status"].astype(str).str.strip()

    for col in ["Staff Name", "Service", "Customer Email", "Customer Name"]:
        if col in df_source.columns:
            df_source[col] = df_source[col].astype(str).str.strip()

    if "Attendance Duration (mins)" in df_source.columns:
        df_source["Attendance Duration (mins)"] = pd.to_numeric(
            df_source["Attendance Duration (mins)"], errors="coerce"
        )

    # Normalize staff names
    known_staff_map = {
        "shahd ayman": "Shahd Ayman",
    }

    if "Staff Name" in df_source.columns:
        staff_clean = df_source["Staff Name"].astype(str).str.strip().str.lower()
        df_source["Staff Name"] = staff_clean.replace(known_staff_map)

    # Fix Shahd Ayman appearing as Customer Name when Staff Name is empty
    if "Customer Name" in df_source.columns and "Staff Name" in df_source.columns:
        customer_clean = df_source["Customer Name"].astype(str).str.strip().str.lower()
        mask_shahd_customer = customer_clean.eq("shahd ayman")
        mask_staff_missing = (
            df_source["Staff Name"].isna() |
            df_source["Staff Name"].astype(str).str.strip().eq("") |
            df_source["Staff Name"].astype(str).str.strip().str.lower().eq("nan")
        )
        df_source.loc[mask_shahd_customer & mask_staff_missing, "Staff Name"] = "Shahd Ayman"

    if "Hour" in df_source.columns:
        df_source["Day Period"] = df_source["Hour"].apply(classify_hour)
    else:
        df_source["Day Period"] = "Unknown"

    # ══════════════════════════════════════════════════════════════════
    # 4) Filters
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🔍 Filters</div>', unsafe_allow_html=True)

    month_opts = sorted(df_source["Month"].dropna().unique().tolist()) if "Month" in df_source.columns else []
    status_opts = sorted(df_source["Status"].dropna().unique().tolist()) if "Status" in df_source.columns else []
    staff_opts = sorted(df_source["Staff Name"].dropna().unique().tolist()) if "Staff Name" in df_source.columns else []
    service_opts = sorted(df_source["Service"].dropna().unique().tolist()) if "Service" in df_source.columns else []

    f1, f2, f3, f4 = st.columns(4)
    sel_m = f1.multiselect("Month", month_opts, default=month_opts)
    sel_s = f2.multiselect("Status", status_opts, default=status_opts)
    sel_st = f3.multiselect("Staff", staff_opts, default=staff_opts)
    sel_sv = f4.multiselect("Service", service_opts, default=service_opts)

    filtered_df = df_source.copy()
    if sel_m and "Month" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Month"].isin(sel_m)]
    if sel_s and "Status" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Status"].isin(sel_s)]
    if sel_st and "Staff Name" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Staff Name"].isin(sel_st)]
    if sel_sv and "Service" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Service"].isin(sel_sv)]

    if filtered_df.empty:
        st.warning("No data for selected filters.")
        return

    # ══════════════════════════════════════════════════════════════════
    # 5) Customer-safe dataframe
    # ══════════════════════════════════════════════════════════════════
    customer_df = filtered_df.copy()

    if "Customer Name" in customer_df.columns:
        customer_df = customer_df[
            ~customer_df["Customer Name"].astype(str).str.strip().str.lower().eq("shahd ayman")
        ]

    if "Customer Email" in customer_df.columns:
        customer_df = customer_df[
            ~customer_df["Customer Email"].astype(str).str.strip().str.lower().str.contains("shahd", na=False)
        ]

    # ══════════════════════════════════════════════════════════════════
    # 6) KPI Calculations
    # ══════════════════════════════════════════════════════════════════
    total_bookings = len(filtered_df)

    done_count = int((filtered_df["Status"] == "Done").sum()) if "Status" in filtered_df.columns else 0
    review_count = int((filtered_df["Status"] == "Review").sum()) if "Status" in filtered_df.columns else 0
    booked_count = int((filtered_df["Status"] == "Booked").sum()) if "Status" in filtered_df.columns else 0

    attendance_rate = round((done_count / total_bookings) * 100, 1) if total_bookings else 0

    dur_col = "Customer Duration Minutes"
    if dur_col in filtered_df.columns and not filtered_df[dur_col].isna().all():
        valid_durations = filtered_df.loc[filtered_df[dur_col] > 0, dur_col]
        avg_duration = round(valid_durations.mean(), 1) if not valid_durations.empty else 0
    else:
        avg_duration = 0

    unique_cust = customer_df["Customer Email"].nunique() if "Customer Email" in customer_df.columns else 0

    pending_count = int(total_bookings - done_count)
    completion_gap = int(booked_count - done_count)
    no_show_rate = round((completion_gap / booked_count) * 100, 1) if booked_count > 0 else 0

    customer_counts = (
        customer_df["Customer Email"].value_counts()
        if "Customer Email" in customer_df.columns else pd.Series(dtype=int)
    )
    repeat_customers = int((customer_counts > 1).sum()) if not customer_counts.empty else 0
    new_customers = int((customer_counts == 1).sum()) if not customer_counts.empty else 0
    repeat_ratio = round((repeat_customers / unique_cust) * 100, 1) if unique_cust else 0

    # ══════════════════════════════════════════════════════════════════
    # 7) KPIs - Row 1
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">📈 Key Metrics</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(vertical_kpi(total_bookings, "Total Bookings", T['accent'], "📋"), unsafe_allow_html=True)
    with col2:
        st.markdown(vertical_kpi(done_count, "Done", T['green'], "✅"), unsafe_allow_html=True)
    with col3:
        st.markdown(vertical_kpi(review_count, "Review", T['amber'], "📝"), unsafe_allow_html=True)
    with col4:
        st.markdown(vertical_kpi(booked_count, "Booked", T['muted'], "📌"), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # 8) KPIs - Row 2
    # ══════════════════════════════════════════════════════════════════
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(vertical_kpi(f"{attendance_rate}%", "Attendance Rate", T['accent2'], "🎯"), unsafe_allow_html=True)
    with col6:
        st.markdown(vertical_kpi(f"{avg_duration}m", "Avg Duration", T['text'], "⏱️"), unsafe_allow_html=True)
    with col7:
        st.markdown(vertical_kpi(unique_cust, "Unique Customers", T['red'], "👥"), unsafe_allow_html=True)
    with col8:
        st.markdown(vertical_kpi(f"{no_show_rate}%", "No-Show Risk", T['amber'], "🚫"), unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # 9) KPIs - Row 3
    # ══════════════════════════════════════════════════════════════════
    col9, col10, col11, col12 = st.columns(4)
    with col9:
        st.markdown(vertical_kpi(pending_count, "Pending / Not Done", T['muted'], "⌛"), unsafe_allow_html=True)
    with col10:
        st.markdown(vertical_kpi(completion_gap, "Booked-Done Gap", T['red'], "📉"), unsafe_allow_html=True)
    with col11:
        st.markdown(vertical_kpi(repeat_customers, "Repeat Customers", T['green'], "🔁"), unsafe_allow_html=True)
    with col12:
        st.markdown(vertical_kpi(f"{repeat_ratio}%", "Repeat Ratio", T['accent'], "🧠"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # 10) Aggregations
    # ══════════════════════════════════════════════════════════════════
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    monthly = (
        filtered_df.groupby(["Month Start", "Month"])
        .size()
        .reset_index(name="Bookings")
        .sort_values("Month Start")
        if {"Month Start", "Month"}.issubset(filtered_df.columns)
        else pd.DataFrame(columns=["Month Start", "Month", "Bookings"])
    )

    status_df = (
        filtered_df.groupby("Status").size().reset_index(name="Count")
        if "Status" in filtered_df.columns else pd.DataFrame(columns=["Status", "Count"])
    )

    by_day = (
        filtered_df.groupby("Day Name").size().reindex(day_order, fill_value=0).reset_index()
        if "Day Name" in filtered_df.columns else pd.DataFrame(columns=["Day", "Bookings"])
    )
    if not by_day.empty:
        by_day.columns = ["Day", "Bookings"]

    by_time = (
        filtered_df.groupby(["Hour", "Time Slot"]).size().reset_index(name="Bookings").sort_values(["Hour", "Time Slot"])
        if {"Hour", "Time Slot"}.issubset(filtered_df.columns)
        else pd.DataFrame(columns=["Hour", "Time Slot", "Bookings"])
    )

    by_staff = (
        filtered_df.groupby("Staff Name").size().reset_index(name="Bookings").sort_values("Bookings", ascending=False)
        if "Staff Name" in filtered_df.columns else pd.DataFrame(columns=["Staff Name", "Bookings"])
    )

    by_service = (
        filtered_df.groupby("Service").size().reset_index(name="Bookings").sort_values("Bookings", ascending=False)
        if "Service" in filtered_df.columns else pd.DataFrame(columns=["Service", "Bookings"])
    )

    by_period = (
        filtered_df.groupby("Day Period").size().reset_index(name="Bookings")
        if "Day Period" in filtered_df.columns else pd.DataFrame(columns=["Day Period", "Bookings"])
    )

    # Staff Performance
    if {"Staff Name", "Status"}.issubset(filtered_df.columns):
        agg_dict = {
            "Completed": ("Status", lambda x: (x == "Done").sum()),
            "Total": ("Status", "count"),
        }
        if "Attendance Duration (mins)" in filtered_df.columns:
            agg_dict["Avg_Duration"] = ("Attendance Duration (mins)", "mean")

        staff_perf = filtered_df.groupby("Staff Name").agg(**agg_dict).reset_index()
        staff_perf["Efficiency %"] = np.where(
            staff_perf["Total"] > 0,
            (staff_perf["Completed"] / staff_perf["Total"]) * 100,
            0
        )
        if "Avg_Duration" in staff_perf.columns:
            staff_perf["Avg_Duration"] = staff_perf["Avg_Duration"].fillna(0).round(1)
        staff_perf = staff_perf.sort_values(["Efficiency %", "Completed"], ascending=[False, False])
    else:
        staff_perf = pd.DataFrame(columns=["Staff Name", "Completed", "Total", "Avg_Duration", "Efficiency %"])

    # Top Customers
    if "Customer Email" in customer_df.columns:
        cust_agg = {
            "Bookings": ("Customer Email", "count"),
        }
        if "Status" in customer_df.columns:
            cust_agg["Done"] = ("Status", lambda x: (x == "Done").sum())
        if "Date Time" in customer_df.columns:
            cust_agg["Last_Booking"] = ("Date Time", "max")

        top_customers = (
            customer_df.groupby("Customer Email")
            .agg(**cust_agg)
            .reset_index()
            .sort_values("Bookings", ascending=False)
        )
    else:
        top_customers = pd.DataFrame(columns=["Customer Email", "Bookings", "Done", "Last_Booking"])

    # Heatmap
    if {"Day Name", "Hour"}.issubset(filtered_df.columns):
        heatmap_df = (
            filtered_df.groupby(["Day Name", "Hour"])
            .size()
            .reset_index(name="Bookings")
        )
        heatmap_df["Day Name"] = pd.Categorical(heatmap_df["Day Name"], categories=day_order, ordered=True)
        heatmap_df = heatmap_df.sort_values(["Day Name", "Hour"])
    else:
        heatmap_df = pd.DataFrame(columns=["Day Name", "Hour", "Bookings"])

    # Funnel
    funnel_df = pd.DataFrame({
        "Stage": ["Booked", "Review", "Done"],
        "Count": [booked_count, review_count, done_count]
    })

    # Forecast
    forecast_df = monthly.copy()
    if not forecast_df.empty:
        forecast_df["Rolling Avg (2)"] = forecast_df["Bookings"].rolling(2, min_periods=1).mean().round(1)
        forecast_df["Rolling Avg (3)"] = forecast_df["Bookings"].rolling(3, min_periods=1).mean().round(1)

    # ══════════════════════════════════════════════════════════════════
    # 11) Visual Analysis - Row 1
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">📉 Visual Analysis</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_month = px.line(monthly, x="Month Start", y="Bookings", markers=True, title="Bookings Trend by Month")
        fig_month.update_traces(line_color=T['accent'])
        fig_month = plotly_layout(fig_month)
        st.plotly_chart(fig_month, use_container_width=True)

    with c2:
        fig_status = px.pie(status_df, names="Status", values="Count", title="Bookings by Status", hole=0.45)
        fig_status.update_traces(marker_colors=[T['accent'], T['green'], T['amber'], T['red'], T['muted']])
        fig_status = plotly_layout(fig_status)
        st.plotly_chart(fig_status, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # 12) Visual Analysis - Row 2
    # ══════════════════════════════════════════════════════════════════
    c3, c4 = st.columns(2)
    with c3:
        fig_day = px.bar(by_day, x="Day", y="Bookings", title="Bookings by Day")
        fig_day.update_traces(marker_color=T['accent'])
        fig_day = plotly_layout(fig_day)
        st.plotly_chart(fig_day, use_container_width=True)

    with c4:
        fig_time = px.bar(by_time, x="Time Slot", y="Bookings", title="Bookings by Time Slot")
        fig_time.update_traces(marker_color=T['green'])
        fig_time = plotly_layout(fig_time)
        st.plotly_chart(fig_time, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # 13) Visual Analysis - Row 3
    # ══════════════════════════════════════════════════════════════════
    c5, c6 = st.columns(2)
    with c5:
        fig_staff = px.bar(by_staff.head(15), x="Staff Name", y="Bookings", title="Top Staff by Booking Volume")
        fig_staff.update_traces(marker_color=T['amber'])
        fig_staff = plotly_layout(fig_staff)
        st.plotly_chart(fig_staff, use_container_width=True)

    with c6:
        fig_service = px.bar(by_service.head(15), x="Service", y="Bookings", title="Top Services by Demand")
        fig_service.update_traces(marker_color=T['red'])
        fig_service = plotly_layout(fig_service)
        st.plotly_chart(fig_service, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # 14) Visual Analysis - Row 4
    # ══════════════════════════════════════════════════════════════════
    c7, c8 = st.columns(2)
    with c7:
        fig_period = px.bar(by_period, x="Day Period", y="Bookings", title="Peak Time Analysis")
        fig_period.update_traces(marker_color=T['accent2'])
        fig_period = plotly_layout(fig_period)
        st.plotly_chart(fig_period, use_container_width=True)

    with c8:
        fig_funnel = px.funnel(funnel_df, x="Count", y="Stage", title="Booking Funnel")
        fig_funnel = plotly_layout(fig_funnel)
        st.plotly_chart(fig_funnel, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # 15) Visual Analysis - Row 5
    # ══════════════════════════════════════════════════════════════════
    c9, c10 = st.columns(2)
    with c9:
        if not heatmap_df.empty:
            fig_heat = px.density_heatmap(
                heatmap_df,
                x="Hour",
                y="Day Name",
                z="Bookings",
                title="Bookings Heatmap (Day vs Hour)",
                color_continuous_scale="Reds"
            )
            fig_heat = plotly_layout(fig_heat)
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Heatmap unavailable for current filters.")

    with c10:
        if not staff_perf.empty:
            hover_cols = ["Completed", "Total"]
            if "Avg_Duration" in staff_perf.columns:
                hover_cols.append("Avg_Duration")

            fig_eff = px.bar(
                staff_perf.head(15),
                x="Staff Name",
                y="Efficiency %",
                hover_data=hover_cols,
                title="Staff Efficiency (%)"
            )
            fig_eff.update_traces(marker_color=T['green'])
            fig_eff = plotly_layout(fig_eff)
            st.plotly_chart(fig_eff, use_container_width=True)
        else:
            st.info("Staff efficiency unavailable for current filters.")

    # ══════════════════════════════════════════════════════════════════
    # 16) Visual Analysis - Row 6
    # ══════════════════════════════════════════════════════════════════
    c11, c12 = st.columns(2)
    with c11:
        customer_seg_df = pd.DataFrame({
            "Segment": ["New Customers", "Repeat Customers"],
            "Count": [new_customers, repeat_customers]
        })
        fig_customer_seg = px.pie(
            customer_seg_df,
            names="Segment",
            values="Count",
            title="Customer Mix: New vs Repeat",
            hole=0.45
        )
        fig_customer_seg.update_traces(marker_colors=[T['accent'], T['green']])
        fig_customer_seg = plotly_layout(fig_customer_seg)
        st.plotly_chart(fig_customer_seg, use_container_width=True)

    with c12:
        if not forecast_df.empty:
            fig_forecast = px.line(
                forecast_df,
                x="Month Start",
                y=["Bookings", "Rolling Avg (2)", "Rolling Avg (3)"],
                markers=True,
                title="Bookings Trend + Simple Forecast Signal"
            )
            fig_forecast = plotly_layout(fig_forecast)
            st.plotly_chart(fig_forecast, use_container_width=True)
        else:
            st.info("Forecast unavailable for current filters.")

    # ══════════════════════════════════════════════════════════════════
    # 17) Scatter Plot
    # ══════════════════════════════════════════════════════════════════
    if "Attendance Duration (mins)" in filtered_df.columns and "Hour" in filtered_df.columns and "Status" in filtered_df.columns:
        scatter_df = filtered_df.dropna(subset=["Attendance Duration (mins)", "Hour"]).copy()
        if not scatter_df.empty:
            hover_cols = [c for c in ["Staff Name", "Service"] if c in scatter_df.columns]
            fig_scatter = px.scatter(
                scatter_df,
                x="Attendance Duration (mins)",
                y="Hour",
                color="Status",
                hover_data=hover_cols if hover_cols else None,
                title="Duration vs Booking Hour Analysis"
            )
            fig_scatter = plotly_layout(fig_scatter)
            st.plotly_chart(fig_scatter, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # 18) Advanced Insights
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🧠 Advanced Insights</div>', unsafe_allow_html=True)

    top_month = monthly.sort_values("Bookings", ascending=False).iloc[0]["Month"] if not monthly.empty else "N/A"
    top_day = by_day.sort_values("Bookings", ascending=False).iloc[0]["Day"] if not by_day.empty else "N/A"
    top_staff = by_staff.iloc[0]["Staff Name"] if not by_staff.empty else "N/A"
    top_service = by_service.iloc[0]["Service"] if not by_service.empty else "N/A"
    peak_period = by_period.sort_values("Bookings", ascending=False).iloc[0]["Day Period"] if not by_period.empty else "N/A"
    weakest_staff = staff_perf.sort_values(["Efficiency %", "Total"], ascending=[True, False]).iloc[0]["Staff Name"] if not staff_perf.empty else "N/A"

    col_i1, col_i2, col_i3 = st.columns(3)

    with col_i1:
        st.success(f"🗓️ Top Month: {top_month}")
        st.success(f"📆 Peak Day: {top_day}")
        st.info(f"⏰ Peak Period: {peak_period}")
        st.warning(f"🚫 No-Show Rate: {no_show_rate}%")

    with col_i2:
        st.success(f"👨‍🏫 Top Staff by Volume: {top_staff}")
        st.info(f"📉 Weakest Staff Efficiency: {weakest_staff}")
        st.success(f"🛠️ Top Service: {top_service}")
        st.info(f"🔁 Repeat Customers: {repeat_customers}")

    with col_i3:
        st.success(f"🎯 Attendance Rate: {attendance_rate}%")
        st.warning(f"⌛ Pending / Not Done: {pending_count}")
        st.error(f"📉 Booked-to-Done Gap: {completion_gap}")
        st.info(f"🧠 Repeat Ratio: {repeat_ratio}%")

    # Executive Insight Box
    summary_parts = []
    if top_day != "N/A":
        summary_parts.append(f"Highest demand appears on **{top_day}**")
    if peak_period != "N/A":
        summary_parts.append(f"the strongest traffic window is **{peak_period}**")
    if top_staff != "N/A":
        summary_parts.append(f"the highest booking volume is handled by **{top_staff}**")
    if top_service != "N/A":
        summary_parts.append(f"and the most requested service is **{top_service}**")

    if summary_parts:
        st.markdown(
            f"""
            <div style="
                background:{T['surface']};
                border:1px solid {T['border']};
                border-left:5px solid {T['accent']};
                border-radius:14px;
                padding:16px;
                margin-top:10px;
                color:{T['text']};">
                💡 <b>Executive Insight:</b> {", ".join(summary_parts)}.
                Current attendance completion is <b>{attendance_rate}%</b>, while no-show risk is <b>{no_show_rate}%</b>.
                Repeat customer share stands at <b>{repeat_ratio}%</b>.
            </div>
            """,
            unsafe_allow_html=True
        )

    # ══════════════════════════════════════════════════════════════════
    # 19) Detailed Tables - 6 Tabs
    # ══════════════════════════════════════════════════════════════════
    st.markdown('<div class="section-title">🗃️ Detailed Records</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "✅ Matched / Done",
        "⏳ Pending",
        "👥 Top Customers",
        "👨‍🏫 Staff Performance",
        "🧩 Status Pivot",
        "📊 Raw Data"
    ])

    with tab1:
        done_df = filtered_df[filtered_df["Status"] == "Done"].copy() if "Status" in filtered_df.columns else pd.DataFrame()
        st.dataframe(done_df, use_container_width=True)

    with tab2:
        pending_df = filtered_df[filtered_df["Status"] != "Done"].copy() if "Status" in filtered_df.columns else pd.DataFrame()
        st.dataframe(pending_df, use_container_width=True)

    with tab3:
        st.dataframe(top_customers.head(25), use_container_width=True)

    with tab4:
        st.dataframe(staff_perf.head(25), use_container_width=True)

    with tab5:
        if {"Staff Name", "Status"}.issubset(filtered_df.columns):
            pivot = pd.pivot_table(
                filtered_df,
                index="Staff Name",
                columns="Status",
                aggfunc="size",
                fill_value=0
            ).reset_index()
            st.dataframe(pivot, use_container_width=True)
        else:
            st.info("Status pivot unavailable.")

    with tab6:
        st.dataframe(filtered_df, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # 20) Download
    # ══════════════════════════════════════════════════════════════════
    st.markdown("<br>", unsafe_allow_html=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, sheet_name="Filtered_Bookings", index=False)

        if not staff_perf.empty:
            staff_perf.to_excel(writer, sheet_name="Staff_Performance", index=False)

        if not top_customers.empty:
            top_customers.to_excel(writer, sheet_name="Top_Customers", index=False)

        if {"Staff Name", "Status"}.issubset(filtered_df.columns):
            pivot = pd.pivot_table(
                filtered_df,
                index="Staff Name",
                columns="Status",
                aggfunc="size",
                fill_value=0
            ).reset_index()
            pivot.to_excel(writer, sheet_name="Status_Pivot", index=False)

        if not monthly.empty:
            monthly.to_excel(writer, sheet_name="Monthly_Trend", index=False)

        if not heatmap_df.empty:
            heatmap_df.to_excel(writer, sheet_name="Day_Hour_Heatmap", index=False)

    output.seek(0)

    st.download_button(
        "⬇️ Download filtered Excel",
        data=output.getvalue(),
        file_name="dashboard_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )