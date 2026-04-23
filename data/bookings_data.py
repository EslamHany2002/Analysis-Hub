"""
Bookings Attendance Data Loader
"""

import pandas as pd
import streamlit as st


@st.cache_data
def load_bookings_excel(file):
    """
    Load bookings Excel file with multiple sheets.
    
    Args:
        file: File object from uploader
        
    Returns:
        dict: Dictionary of sheet_name -> DataFrame
    """
    xls = pd.ExcelFile(file)
    sheets = {}
    for sheet in xls.sheet_names:
        sheets[sheet] = pd.read_excel(file, sheet_name=sheet)
    return sheets


def prepare_bookings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare bookings DataFrame for analysis.
    
    Args:
        df: Raw bookings DataFrame
        
    Returns:
        pd.DataFrame: Processed bookings data
    """
    df = df.copy()

    # Parse datetime and extract features
    if "Date Time" in df.columns:
        df["Date Time"] = pd.to_datetime(df["Date Time"], errors="coerce")
        df["Date"] = df["Date Time"].dt.date
        df["Month"] = df["Date Time"].dt.to_period("M").astype(str)
        df["Month Start"] = df["Date Time"].dt.to_period("M").dt.to_timestamp()
        df["Day Name"] = df["Date Time"].dt.day_name()
        df["Hour"] = df["Date Time"].dt.hour
        df["Time Slot"] = df["Date Time"].dt.strftime("%H:%M")

    # Parse attendance meeting time
    if "Attendance Meeting Start" in df.columns:
        df["Attendance Meeting Start"] = pd.to_datetime(
            df["Attendance Meeting Start"], errors="coerce"
        )

    # Parse numeric columns
    numeric_cols = [
        "Duration (mins.)",
        "Attendance Match Score",
        "Attendance Participants Count",
        "Attendance Duration (mins)",
        "Attendance Join Count",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Default status
    if "Status" not in df.columns:
        df["Status"] = "Pending"
    df["Status"] = df["Status"].fillna("Pending")

    # Attendance flag
    if "Attendance Duration (mins)" in df.columns:
        df["Attended Flag"] = df["Attendance Duration (mins)"].fillna(0).gt(0)
    else:
        df["Attended Flag"] = False

    # Fill missing values
    fill_cols = {
        "Customer Email": "Unknown",
        "Customer Name": "Unknown",
        "Service": "Unknown",
        "Staff Name": "Unknown",
    }
    for col, default in fill_cols.items():
        if col in df.columns:
            df[col] = df[col].fillna(default)

    return df