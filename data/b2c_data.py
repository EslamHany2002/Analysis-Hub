"""
B2C Executive Review Data Loader
"""

import numpy as np
import pandas as pd
import streamlit as st
from io import BytesIO

from config.constants import EVAL_AR_COLS, YES_VALUES, NO_VALUES
from core.sentiment import analyze_sentiment_label


def clean_col_name(col: str) -> str:
    """Clean column name from special characters."""
    return str(col).replace("\xa0", " ").strip()


def normalize_text(v):
    """Normalize text values."""
    if pd.isna(v):
        return np.nan
    return str(v).replace("\xa0", " ").strip()


def yes_no_normalize(v):
    """Normalize yes/no values to standard Yes/No."""
    if pd.isna(v):
        return np.nan
    s = str(v).strip().lower().replace("\xa0", " ")
    if s in {x.lower() for x in YES_VALUES}:
        return "Yes"
    if s in {x.lower() for x in NO_VALUES}:
        return "No"
    return str(v).strip()


@st.cache_data(show_spinner=False)
def load_b2c_data(file_bytes):
    """
    Load and process B2C executive review Excel data.
    
    Args:
        file_bytes: Raw bytes from file uploader
        
    Returns:
        pd.DataFrame: Cleaned and processed B2C data
    """
    df = pd.read_excel(BytesIO(file_bytes))
    df.columns = [clean_col_name(c) for c in df.columns]
    
    # Rename Arabic columns to English
    df = df.rename(columns={
        "اسم المحاضر": "Instructor",
        "اسم المجموعة": "Group",
        "تاريخ السيشن": "Session Date",
        "درجة تفاعل الطلاب": "Student Interaction Rate",
        "عدد الطلاب الحاضرين": "Attendance",
        "هل تم الالتزام بالوقت المحدد للسيشن؟": "On Time",
        "السيشن بدات": "Session Started At",
        "السيشن خلصت": "Session Ended At",
        "ليه حصل كده": "Reason",
        "السيشن": "Session Mode",
        "هل الطلاب بدوا فاهمين المحتوى؟": "Students Understood",
        "هل اتعمل تمرين عملي أو مثال تطبيقي؟": "Practical Exercise",
        "هل الطلاب شاركوا في الحل؟": "Students Participated",
        "هل توصي باستمرار المحاضر بنفس المجموعة؟": "Recommend Continuation",
        "اكتب اى حاجه محتاجها": "Open Feedback",
    })

    # Normalize text columns
    text_cols = [
        "Instructor", "Group", "Session Mode", "Reason", 
        "Students Understood", "Practical Exercise", 
        "Students Participated", "Recommend Continuation", 
        "Open Feedback", "Name", "Email"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    # Parse dates
    date_cols = [
        "Start time", "Completion time", "Last modified time",
        "Session Date", "Session Started At", "Session Ended At"
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Parse numeric columns
    numeric_cols = EVAL_AR_COLS + ["Attendance", "Student Interaction Rate"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalize yes/no columns
    yn_cols = [
        "On Time", "Students Understood", "Practical Exercise",
        "Students Participated", "Recommend Continuation"
    ]
    for col in yn_cols:
        if col in df.columns:
            df[col] = df[col].apply(yes_no_normalize)

    # Calculate instructor evaluation
    eval_cols = [c for c in EVAL_AR_COLS if c in df.columns]
    if eval_cols:
        df["Instructor Evaluation"] = df[eval_cols].mean(axis=1).round(2)

    # Calculate response time
    if "Start time" in df.columns and "Completion time" in df.columns:
        df["Response Time (sec)"] = (df["Completion time"] - df["Start time"]).dt.total_seconds()

    # Calculate session duration
    if "Session Started At" in df.columns and "Session Ended At" in df.columns:
        df["Session Duration (min)"] = ((df["Session Ended At"] - df["Session Started At"]).dt.total_seconds() / 60).round(1)

    # Sentiment analysis on feedback
    _add_sentiment_analysis(df)

    return df


def _add_sentiment_analysis(df):
    """Add sentiment labels and scores to feedback columns."""
    text_parts = []
    
    if "Open Feedback" in df.columns:
        text_parts.append(df["Open Feedback"].fillna(""))
    if "Reason" in df.columns:
        text_parts.append(df["Reason"].fillna(""))

    if text_parts:
        combined = text_parts[0].astype(str)
        for s in text_parts[1:]:
            combined = combined + " | " + s.astype(str)
        
        labels_scores = combined.apply(analyze_sentiment_label)
        df["Feedback Sentiment"] = labels_scores.apply(lambda x: x[0])
        df["Feedback Sentiment Score"] = labels_scores.apply(lambda x: x[1])