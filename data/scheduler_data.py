"""
Instructor Scheduler Data Loader
"""

import io
import pandas as pd

from config.constants import ALL_DAYS


def fmt_time(t: str) -> str:
    """Format time string to 12-hour format."""
    try:
        p = str(t).split(":")
        h, m = int(p[0]), int(p[1])
        return f"{h % 12 or 12}:{m:02d} {'AM' if h < 12 else 'PM'}"
    except Exception:
        return str(t)


def time_to_min(t: str) -> int:
    """Convert time string to minutes since midnight."""
    try:
        p = str(t).split(":")
        return int(p[0]) * 60 + int(p[1])
    except Exception:
        return 0


def intervals_overlap(f1, t1, f2, t2) -> bool:
    """Check if two time intervals overlap."""
    return time_to_min(f1) < time_to_min(t2) and time_to_min(f2) < time_to_min(t1)


def recompute(data: dict) -> dict:
    """Recompute derived fields for instructor schedule data."""
    busy = set(g["day"] for g in data["groups"])
    data["off_days"] = [d for d in ALL_DAYS if d not in busy]
    data["busy_days"] = [d for d in ALL_DAYS if d in busy]
    
    uq = {}
    for g in data["groups"]:
        uq.setdefault(g["group"], []).append({
            "day": g["day"],
            "from": g["from"],
            "to": g["to"]
        })
    data["unique_groups"] = uq
    
    return data


def load_schedule_excel(file_bytes: bytes) -> dict:
    """
    Load instructor schedule from Excel file.
    
    Args:
        file_bytes: Raw bytes from file uploader
        
    Returns:
        dict: Instructor schedule data
    """
    xf = pd.ExcelFile(io.BytesIO(file_bytes))
    df = xf.parse("Summary")
    df.columns = [str(c).strip() for c in df.columns]
    
    for col in ["Track", "Instructor", "Group", "Day", "From", "To"]:
        df[col] = df[col].astype(str).str.strip()
    
    df = df[df["Instructor"].notna() & ~df["Instructor"].isin(["nan", "Instructor"])]
    
    instructors = {}
    for _, row in df.iterrows():
        n = row["Instructor"]
        if n not in instructors:
            instructors[n] = {"track": row["Track"], "groups": []}
        instructors[n]["groups"].append({
            "group": row["Group"],
            "day": row["Day"],
            "from": row["From"],
            "to": row["To"]
        })
    
    for n in instructors:
        instructors[n] = recompute(instructors[n])
    
    return instructors