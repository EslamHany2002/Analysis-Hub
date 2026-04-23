"""
Team Performance Data Loader
"""

import numpy as np
import pandas as pd
import streamlit as st

from config.constants import DAILY_TARGET_HOURS, LATE_ENTRY_THRESHOLD


def parse_duration(d):
    """Parse duration string 'H:MM' to float hours."""
    try:
        h, m = str(d).strip().split(":")
        return int(h) + int(m) / 60
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_team_data(file_bytes):
    """
    Load and process team performance Excel data.
    
    Returns:
        tuple: (df, daily, emp, team_daily, days_under, days_over, not_reviewed, late_df)
    """
    df_raw = pd.read_excel(file_bytes)
    df = df_raw.copy()

    # Parse duration
    if "Duration (Hours)" in df.columns:
        df["Duration_Hours"] = df["Duration (Hours)"].apply(parse_duration)
    else:
        df["Duration_Hours"] = np.nan

    # Parse dates
    date_cols = ["Date", "Created At", "Technical Reviewed At", "KPI Reviewed At"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.NaT

    # Calculate late entry
    if {"Created At", "Date"}.issubset(df.columns):
        df["Entry_Delay_Hours"] = (df["Created At"] - df["Date"]).dt.total_seconds() / 3600
        df["Late_Entry"] = df["Entry_Delay_Hours"] > LATE_ENTRY_THRESHOLD
    else:
        df["Entry_Delay_Hours"] = np.nan
        df["Late_Entry"] = False

    # Daily aggregation
    daily = _compute_daily_stats(df)
    
    # Employee stats
    emp = _compute_employee_stats(df, daily)
    
    # Team daily hours
    team_daily = _compute_team_daily(df)
    
    # Summary metrics
    days_under = int((daily["Total_Hours"] < DAILY_TARGET_HOURS - 0.5).sum()) if not daily.empty else 0
    days_over = int((daily["Total_Hours"] > DAILY_TARGET_HOURS + 0.5).sum()) if not daily.empty else 0
    
    not_reviewed = 0
    if "Technical Review" in df.columns and "KPI Review" in df.columns:
        not_reviewed = int(((df["Technical Review"] == "Not Reviewed") & (df["KPI Review"] == "Not Reviewed")).sum())

    late_df = df[df["Late_Entry"]].copy() if "Late_Entry" in df.columns else pd.DataFrame()
    
    return df, daily, emp, team_daily, days_under, days_over, not_reviewed, late_df


def _compute_daily_stats(df):
    """Compute daily statistics per employee."""
    if {"Assigned To", "Date"}.issubset(df.columns):
        daily = (
            df.groupby(["Assigned To", "Date"])
            .agg(Total_Hours=("Duration_Hours", "sum"), Task_Count=(df.columns[0], "count"))
            .reset_index()
        )
    else:
        daily = pd.DataFrame(columns=["Assigned To", "Date", "Total_Hours", "Task_Count"])

    if not daily.empty:
        daily["Status_Flag"] = daily["Total_Hours"].apply(
            lambda h: "🟢 OK" if abs(h - DAILY_TARGET_HOURS) <= 0.5 
            else ("🔴 Less" if h < DAILY_TARGET_HOURS else "🟡 More")
        )
    else:
        daily["Status_Flag"] = []
    
    return daily


def _compute_employee_stats(df, daily):
    """Compute per-employee statistics."""
    # Late entries count
    late_counts = pd.Series(dtype=int)
    if "Assigned To" in df.columns:
        late_counts = df[df["Late_Entry"]].groupby("Assigned To").size().rename("Late_Entries")

    # Daily aggregations per employee
    if not daily.empty:
        emp_daily = daily.groupby("Assigned To").agg(
            Days_Worked=("Date", "nunique"),
            Avg_Hours_Per_Day=("Total_Hours", "mean"),
            Days_Under_8h=("Total_Hours", lambda x: (x < DAILY_TARGET_HOURS).sum()),
            Days_Over_8h=("Total_Hours", lambda x: (x > DAILY_TARGET_HOURS).sum()),
            Max_Daily_Hours=("Total_Hours", "max"),
            Min_Daily_Hours=("Total_Hours", "min"),
        ).reset_index()
    else:
        emp_daily = pd.DataFrame(columns=[
            "Assigned To", "Days_Worked", "Avg_Hours_Per_Day",
            "Days_Under_8h", "Days_Over_8h", "Max_Daily_Hours", "Min_Daily_Hours"
        ])

    # Task aggregations
    emp_tasks = _compute_task_stats(df)

    # Merge all stats
    if not emp_daily.empty and not emp_tasks.empty:
        emp = emp_daily.merge(emp_tasks, on="Assigned To", how="outer").merge(late_counts, on="Assigned To", how="left")
    else:
        emp = emp_tasks.copy() if not emp_tasks.empty else emp_daily.copy()
        if "Assigned To" in emp.columns:
            emp = emp.merge(late_counts, on="Assigned To", how="left")

    # Final calculations
    if not emp.empty:
        emp["Late_Entries"] = emp.get("Late_Entries", 0).fillna(0).astype(int)
        emp["Completion_Rate_%"] = np.where(
            emp["Total_Tasks"].fillna(0) > 0,
            (emp["Completed_Tasks"].fillna(0) / emp["Total_Tasks"].fillna(0) * 100).round(1),
            0
        )
        for c in ["Avg_Hours_Per_Day", "Total_Hours", "Idle_Hours"]:
            if c in emp.columns:
                emp[c] = pd.to_numeric(emp[c], errors="coerce").round(2)

    return emp


def _compute_task_stats(df):
    """Compute task-related statistics per employee."""
    if "Assigned To" not in df.columns:
        return pd.DataFrame(columns=["Assigned To", "Total_Tasks", "Total_Hours", "Completed_Tasks", "Idle_Hours"])

    id_col = "ID" if "ID" in df.columns else df.columns[0]
    
    emp_tasks = df.groupby("Assigned To").agg(
        Total_Tasks=(id_col, "count"),
        Total_Hours=("Duration_Hours", "sum"),
        Completed_Tasks=(
            "Completed",
            lambda x: (x.astype(str) == "Yes").sum()
        ) if "Completed" in df.columns else (id_col, "count"),
    ).reset_index()

    # Idle hours
    if "Task Type" in df.columns:
        idle_hours = df.assign(
            _Idle=np.where(df["Task Type"].astype(str) == "Idle", df["Duration_Hours"], 0)
        ).groupby("Assigned To")["_Idle"].sum().rename("Idle_Hours")
        emp_tasks = emp_tasks.merge(idle_hours, on="Assigned To", how="left")
    else:
        emp_tasks["Idle_Hours"] = 0

    # Status breakdown
    if "Status" in df.columns:
        status_counts = df.pivot_table(
            index="Assigned To", columns="Status", values=id_col, aggfunc="count", fill_value=0
        ).reset_index()
        emp_tasks = emp_tasks.merge(status_counts, on="Assigned To", how="left")

    return emp_tasks


def _compute_team_daily(df):
    """Compute total team hours per day."""
    if "Date" in df.columns:
        team_daily = df.groupby("Date")["Duration_Hours"].sum().reset_index().rename(
            columns={"Duration_Hours": "Team_Hours"}
        )
    else:
        team_daily = pd.DataFrame(columns=["Date", "Team_Hours"])
    
    return team_daily