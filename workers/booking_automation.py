import os
import re
import glob
import time
import json
from difflib import SequenceMatcher
from datetime import datetime, timedelta

import pandas as pd
from playwright.sync_api import sync_playwright


# =========================
# PATHS
# =========================
BASE_DIR = os.getcwd()
BOOKINGS_DIR = os.path.join(BASE_DIR, "my_booking_data")
ATTENDANCE_DIR = os.path.join(BASE_DIR, "attendance_reports")
OUTPUT_FILE = os.path.join(BASE_DIR, "final_merged_analysis.csv")
BOOKINGS_FILE = os.path.join(BOOKINGS_DIR, "BookingsReportingData.tsv")

os.makedirs(BOOKINGS_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)


# =========================
# HELPERS
# =========================
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text).strip().lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = text.replace("-", " ").replace("_", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def similarity(a, b):
    a = normalize_text(a)
    b = normalize_text(b)
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()


def safe_to_datetime(val):
    try:
        return pd.to_datetime(val, errors="coerce")
    except Exception:
        return pd.Na


def parse_duration_to_minutes(duration_text):
    if pd.isna(duration_text):
        return 0.0

    text = str(duration_text).strip().lower()
    hours = minutes = seconds = 0

    h_match = re.search(r"(\d+)\s*h", text)
    m_match = re.search(r"(\d+)\s*m", text)
    s_match = re.search(r"(\d+)\s*s", text)

    if h_match:
        hours = int(h_match.group(1))
    if m_match:
        minutes = int(m_match.group(1))
    if s_match:
        seconds = int(s_match.group(1))

    return hours * 60 + minutes + (seconds / 60.0)


def extract_customer_name_from_title(meeting_title):
    if not meeting_title:
        return ""
    title = str(meeting_title).strip()
    if " - " in title:
        return title.split(" - ", 1)[1].strip()
    return title.strip()


def get_target_meetings_from_bookings(bookings_file):
    df = load_bookings(bookings_file).copy()
    df = df.dropna(subset=["booking_datetime"])

    targets = []
    for _, row in df.iterrows():
        booking_dt = row.get("booking_datetime")

        targets.append({
            "booking_id": row.get("Booking Id", ""),
            "customer_name": row.get("Customer Name", ""),
            "customer_email": row.get("Customer Email", ""),
            "staff_name": row.get("Staff Name", ""),
            "staff_email": row.get("Staff Email", ""),
            "service": row.get("Service", ""),
            "booking_datetime": booking_dt,
            "booking_date": booking_dt.date() if pd.notna(booking_dt) else None,
        })

    return targets


def open_attendance_and_download(page, booking_id=""):
    print("[Auto] Trying Attendance tab or overflow + menu...")

    attendance_opened = False

    # =========================
    # 1) جرّب Attendance المباشر
    # =========================
    direct_attendance = [
        page.get_by_role("tab", name=re.compile(r"^Attendance$", re.I)),
        page.get_by_role("button", name=re.compile(r"^Attendance$", re.I)),
        page.get_by_text("Attendance", exact=True),
        page.locator('[role="tab"]').filter(has_text=re.compile(r'^Attendance$', re.I)),
    ]

    for sel in direct_attendance:
        try:
            if sel.count() > 0 and sel.first.is_visible():
                sel.first.click()
                time.sleep(2)
                attendance_opened = True
                print("[Auto] Attendance opened directly")
                break
        except Exception:
            continue

    # =========================
    # 2) لو مش ظاهر، افتحه من overflow + button
    # =========================
    if not attendance_opened:
        print("[Auto] Direct Attendance not found, trying overflow button...")

        try:
            overflow_btn = page.locator('[data-tid="tab-overflow-button"]')

            if overflow_btn.count() > 0 and overflow_btn.first.is_visible():
                try:
                    overflow_btn.first.click(timeout=3000)
                    time.sleep(2)
                    print("[Auto] Overflow + button clicked normally")
                except Exception:
                    try:
                        overflow_btn.first.click(force=True, timeout=3000)
                        time.sleep(2)
                        print("[Auto] Overflow + button clicked with force")
                    except Exception:
                        overflow_btn.first.evaluate("(el) => el.click()")
                        time.sleep(2)
                        print("[Auto] Overflow + button clicked via JS")

                attendance_from_menu = [
                    page.get_by_role("menuitem", name=re.compile(r"^Attendance$", re.I)),
                    page.get_by_text("Attendance", exact=True),
                    page.locator('[role="menuitem"]').filter(has_text=re.compile(r'^Attendance$', re.I)),
                    page.get_by_role("button", name=re.compile(r"^Attendance$", re.I)),
                ]

                for sel in attendance_from_menu:
                    try:
                        if sel.count() > 0 and sel.first.is_visible():
                            sel.first.click()
                            time.sleep(2)
                            attendance_opened = True
                            print("[Auto] Attendance opened from overflow menu")
                            break
                    except Exception:
                        continue

        except Exception as e:
            print(f"[Auto] Overflow menu failed: {e}")

    if not attendance_opened:
        print("[Auto] Could not open Attendance")
        return False

    # =========================
    # 3) اضغط Download
    # =========================
    print("[Auto] Trying Download...")

    download_selectors = [
        page.get_by_role("button", name=re.compile(r"^Download$", re.I)),
        page.get_by_text("Download", exact=True),
        page.locator('text=Download').first,
    ]

    for sel in download_selectors:
        try:
            if sel.count() > 0 and sel.first.is_visible():
                with page.expect_download() as info:
                    sel.first.click()

                dl = info.value

                safe_booking_id = re.sub(r'[^A-Za-z0-9_-]+', "_", str(booking_id)) if booking_id else str(int(time.time()))
                safe_name = f"attendance_{safe_booking_id}.csv"

                save_path = os.path.join(ATTENDANCE_DIR, safe_name)
                dl.save_as(save_path)

                print(f"[Auto] Downloaded attendance: {save_path}")
                return True

        except Exception as e:
            print(f"[Auto] Download failed: {e}")
            continue

    print("[Auto] Download button not found")
    return False


def is_meeting_matching_booking(meeting_title, meeting_datetime, booking, tolerance_minutes=30):
    score = 0

    if meeting_title:
        score += similarity(meeting_title, booking.get("service", "")) * 30
        score += similarity(meeting_title, booking.get("customer_name", "")) * 40

    if meeting_datetime and booking.get("booking_datetime") is not None:
        diff = abs((meeting_datetime - booking["booking_datetime"]).total_seconds()) / 60
        if diff <= 10:
            score += 50
        elif diff <= 30:
            score += 35
        elif diff <= 60:
            score += 20

    return score >= 45



# =========================
# STEP 1: DOWNLOAD BOOKINGS
# =========================
def automation_step_1_bookings():
    print("[Auto] Step 1: Downloading Bookings...")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(BASE_DIR, "user_data"),
            headless=False,
            accept_downloads=True,
        )

        page = browser.new_page()
        page.goto("https://bookings.cloud.microsoft/bookings/calendar")
        time.sleep(15)

        try:
            export_button = page.locator('button[aria-label="Export data in a TSV file"]')

            if export_button.count() == 0:
                raise Exception("Export button not found.")

            export_button.click()
            page.wait_for_selector('text="Export recent data?"', timeout=10000)

            with page.expect_download() as download_info:
                page.get_by_text("Export", exact=True).last.click()

            download = download_info.value
            download.save_as(BOOKINGS_FILE)

            print(f"[Auto] Bookings downloaded: {BOOKINGS_FILE}")

        finally:
            browser.close()

    return BOOKINGS_FILE


# =========================
# STEP 2: DOWNLOAD TEAMS ATTENDANCE
# =========================
def automation_step_2_teams():
    print("[Auto] Step 2: Downloading Teams Attendance from Meeting chats...")

    if not os.path.exists(BOOKINGS_FILE):
        raise FileNotFoundError(f"Bookings file not found: {BOOKINGS_FILE}")

    targets = get_target_meetings_from_bookings(BOOKINGS_FILE)
    if not targets:
        print("[Auto] No bookings found.")
        return

    downloaded_booking_ids = set()

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(BASE_DIR, "user_data"),
            headless=False,
            accept_downloads=True,
        )

        page = browser.new_page()
        page.goto("https://teams.cloud.microsoft/")
        time.sleep(12)

        try:
            # افتح Chat من الشريط الجانبي
            try:
                page.get_by_role("button", name=re.compile("Chat", re.I)).click(timeout=15000)
            except Exception:
                print("[Auto] Could not click Chat directly")

            time.sleep(3)

            # افتح Meeting chats tab
            try:
                page.get_by_role("button", name=re.compile(r"Meeting chats", re.I)).click(timeout=10000)
            except Exception:
                try:
                    page.get_by_text("Meeting chats", exact=True).click(timeout=10000)
                except Exception:
                    print("[Auto] Could not open Meeting chats tab")

            time.sleep(3)

            chats = page.locator('[role="treeitem"], [role="listitem"]')
            chat_count = chats.count()

            print(f"[Auto] Found {chat_count} chat items")

            for i in range(chat_count):
                try:
                    chat_item = chats.nth(i)
                    chat_text = chat_item.inner_text(timeout=3000)
                except Exception:
                    continue

                if not chat_text:
                    continue

                chat_text_norm = normalize_text(chat_text)

                selected_booking = None
                best_score = 0

                for booking in targets:
                    if booking["booking_id"] in downloaded_booking_ids:
                        continue

                    score = 0
                    score += similarity(chat_text, booking["customer_name"]) * 70
                    score += similarity(chat_text, booking["service"]) * 20
                    score += similarity(chat_text, booking["staff_name"]) * 10

                    if score > best_score:
                        best_score = score
                        selected_booking = booking

                if selected_booking is None or best_score < 35:
                    continue

                print(f'[Auto] Opening chat: {chat_text} -> matched booking {selected_booking["booking_id"]}')

                try:
                    chat_item.click()
                    time.sleep(3)
                except Exception as e:
                    print(f"[Auto] Failed to open chat: {e}")
                    continue

                # تأكيد إننا داخل الشات الصح
                page_body = ""
                try:
                    page_body = page.locator("body").inner_text(timeout=4000)
                except Exception:
                    pass

                # لو الـ attendance موجودة مباشرة أو من +
                success = open_attendance_and_download(
                    page,
                    booking_id=selected_booking["booking_id"]
                )

                if success:
                    downloaded_booking_ids.add(selected_booking["booking_id"])

                # ارجع لوضع الشات الطبيعي
                try:
                    page.keyboard.press("Escape")
                    time.sleep(1)
                except Exception:
                    pass

            print(f"[Auto] Downloaded reports count: {len(downloaded_booking_ids)}")

        finally:
            browser.close()


# =========================
# ATTENDANCE PARSER
# =========================
def parse_attendance_report(file_path):
    with open(file_path, "r", encoding="utf-16") as f:
        lines = [line.rstrip("\n\r") for line in f]

    meeting_title = None
    start_time = None
    end_time = None
    participants_start_idx = None

    for i, line in enumerate(lines):
        if line.startswith("Meeting title\t"):
            meeting_title = line.split("\t", 1)[1].strip()
        elif line.startswith("Start time\t"):
            start_time = line.split("\t", 1)[1].strip()
        elif line.startswith("End time\t"):
            end_time = line.split("\t", 1)[1].strip()
        elif line.strip() == "2. Participants":
            participants_start_idx = i + 1
            break

    participants = []

    if participants_start_idx is not None and participants_start_idx < len(lines):
        header_line = lines[participants_start_idx]
        expected_header = [
            "Name", "First Join", "Last Leave", "In-Meeting Duration",
            "Email", "Participant ID (UPN)", "Role"
        ]

        if header_line.split("\t") == expected_header:
            for line in lines[participants_start_idx + 1:]:
                if not line.strip():
                    break

                parts = line.split("\t")
                if len(parts) < 7:
                    continue
                if len(parts) > 7:
                    parts = parts[:7]

                participants.append({
                    "participant_name": parts[0].strip(),
                    "first_join": parts[1].strip(),
                    "last_leave": parts[2].strip(),
                    "in_meeting_duration": parts[3].strip(),
                    "participant_email": parts[4].strip(),
                    "participant_upn": parts[5].strip(),
                    "role": parts[6].strip(),
                })

    participants_df = pd.DataFrame(participants)

    if not participants_df.empty:
        participants_df["duration_minutes"] = participants_df["in_meeting_duration"].apply(parse_duration_to_minutes)
        participants_df["participant_name_norm"] = participants_df["participant_name"].apply(normalize_text)
        participants_df["participant_email_norm"] = (
            participants_df["participant_email"].fillna("").astype(str).str.strip().str.lower()
        )
    else:
        participants_df = pd.DataFrame(columns=[
            "participant_name", "first_join", "last_leave", "in_meeting_duration",
            "participant_email", "participant_upn", "role",
            "duration_minutes", "participant_name_norm", "participant_email_norm"
        ])

    return {
        "attendance_file": os.path.basename(file_path),
        "meeting_title": meeting_title or "",
        "meeting_title_norm": normalize_text(meeting_title),
        "meeting_customer_name": extract_customer_name_from_title(meeting_title),
        "meeting_customer_name_norm": normalize_text(extract_customer_name_from_title(meeting_title)),
        "meeting_start_time": safe_to_datetime(start_time),
        "meeting_end_time": safe_to_datetime(end_time),
        "participants_df": participants_df,
    }


# =========================
# LOAD BOOKINGS
# =========================
def load_bookings(bookings_file):
    df = pd.read_csv(bookings_file, sep="\t")

    df["booking_datetime"] = pd.to_datetime(df["Date Time"], errors="coerce")
    df["booking_date"] = df["booking_datetime"].dt.date

    if "Customer Name" not in df.columns:
        df["Customer Name"] = ""
    if "Customer Email" not in df.columns:
        df["Customer Email"] = ""
    if "Staff Name" not in df.columns:
        df["Staff Name"] = ""
    if "Staff Email" not in df.columns:
        df["Staff Email"] = ""
    if "Service" not in df.columns:
        df["Service"] = ""

    df["customer_name_norm"] = df["Customer Name"].apply(normalize_text)
    df["customer_email_norm"] = df["Customer Email"].fillna("").astype(str).str.strip().str.lower()
    df["staff_name_norm"] = df["Staff Name"].apply(normalize_text)
    df["staff_email_norm"] = df["Staff Email"].fillna("").astype(str).str.strip().str.lower()
    df["service_norm"] = df["Service"].fillna("").astype(str).apply(normalize_text)

    return df


# =========================
# MATCH REPORT TO BOOKING
# =========================
def find_best_booking_for_report(report, bookings_df, used_booking_ids):
    if pd.isna(report["meeting_start_time"]):
        candidate_df = bookings_df.copy()
    else:
        report_date = report["meeting_start_time"].date()
        candidate_df = bookings_df[bookings_df["booking_date"] == report_date].copy()

        if candidate_df.empty:
            candidate_df = bookings_df.copy()

    if candidate_df.empty:
        return None

    best_score = -1
    best_idx = None

    for idx, row in candidate_df.iterrows():
        if row["Booking Id"] in used_booking_ids:
            continue

        score = 0
        score += similarity(row["Customer Name"], report["meeting_customer_name"]) * 60
        score += similarity(row["Service"], report["meeting_title"]) * 10

        if not pd.isna(report["meeting_start_time"]) and not pd.isna(row["booking_datetime"]):
            diff_minutes = abs((row["booking_datetime"] - report["meeting_start_time"]).total_seconds()) / 60
            if diff_minutes <= 10:
                score += 30
            elif diff_minutes <= 30:
                score += 20
            elif diff_minutes <= 60:
                score += 10

        if score > best_score:
            best_score = score
            best_idx = idx

    if best_idx is None:
        return None

    if best_score < 35:
        return None

    return best_idx


# =========================
# EVALUATE ATTENDANCE
# =========================
def evaluate_attendance_for_booking(report, booking_row):
    participants_df = report["participants_df"]

    if participants_df.empty:
        return {
            "customer_attended": False,
            "staff_attended": False,
            "customer_duration_minutes": 0.0,
            "staff_duration_minutes": 0.0,
            "matched_customer_participant": "",
            "matched_staff_participant": "",
            "participants_count": 0,
        }

    customer_email = booking_row["customer_email_norm"]
    customer_name = booking_row["customer_name_norm"]
    staff_email = booking_row["staff_email_norm"]
    staff_name = booking_row["staff_name_norm"]

    customer_attended = False
    staff_attended = False
    customer_duration = 0.0
    staff_duration = 0.0
    matched_customer = ""
    matched_staff = ""
    
    staff_aliases = [
        normalize_text(staff_name),
        "eslam hany",
        "shahd ayman",
    ]

    for _, p in participants_df.iterrows():
        p_email = p["participant_email_norm"]
        p_name = p["participant_name_norm"]

        staff_match = False

        # 1) تطابق بالإيميل
        if staff_email and p_email and staff_email == p_email:
            staff_match = True

        # 2) تطابق بالاسم الأصلي من الـ booking
        elif similarity(staff_name, p_name) >= 0.80:
            staff_match = True

        # 3) تطابق بأي alias معروف للـ staff
        else:
            for alias in staff_aliases:
                if not alias:
                    continue

                if p_name == alias or p_name.startswith(alias):
                    staff_match = True
                    break

                if similarity(alias, p_name) >= 0.80:
                    staff_match = True
                    break

        if staff_match:
            staff_attended = True
            staff_duration += p["duration_minutes"]
            if not matched_staff:
                matched_staff = p["participant_name"]

    best_customer_score = 0
    best_customer_name = ""
    best_customer_duration = 0.0

    for _, p in participants_df.iterrows():
        p_email = p["participant_email_norm"]
        p_name = p["participant_name_norm"]

        if p_email and staff_email and p_email == staff_email:
            continue

        score = 0

        if customer_email and p_email and customer_email == p_email:
            score += 100

        name_sim = similarity(customer_name, p_name)
        if name_sim >= 0.75:
            score += 80
        elif name_sim >= 0.60:
            score += 50
        elif name_sim >= 0.45:
            score += 20

        if score > best_customer_score:
            best_customer_score = score
            best_customer_name = p["participant_name"]
            best_customer_duration = p["duration_minutes"]

    if best_customer_score >= 50:
        customer_attended = True
        customer_duration = best_customer_duration
        matched_customer = best_customer_name

    return {
        "customer_attended": customer_attended,
        "staff_attended": staff_attended,
        "customer_duration_minutes": round(customer_duration, 2),
        "staff_duration_minutes": round(staff_duration, 2),
        "matched_customer_participant": matched_customer,
        "matched_staff_participant": matched_staff,
        "participants_count": len(participants_df),
    }


def build_status(customer_attended, staff_attended, attendance_file_found):
    if attendance_file_found:
        if customer_attended and staff_attended:
            return "Done"
        elif customer_attended and not staff_attended:
            return "Customer Joined / Staff Absent"
        elif not customer_attended and staff_attended:
            return "Staff Joined / Customer Absent"
        else:
            return "Absent"
    return "No Attendance Report"


# =========================
# STEP 3: MERGE
# =========================
def automation_step_3_merge():
    print("[Auto] Step 3: Merging data...")

    if not os.path.exists(BOOKINGS_FILE):
        raise FileNotFoundError(f"Bookings file not found: {BOOKINGS_FILE}")

    bookings_df = load_bookings(BOOKINGS_FILE)
    attendance_files = glob.glob(os.path.join(ATTENDANCE_DIR, "*.csv"))

    parsed_reports = []
    for file_path in attendance_files:
        try:
            parsed_reports.append(parse_attendance_report(file_path))
        except Exception as e:
            print(f"⚠️ Failed to parse {file_path}: {e}")

    used_booking_ids = set()
    report_results = []

    for report in parsed_reports:
        best_idx = find_best_booking_for_report(report, bookings_df, used_booking_ids)

        if best_idx is None:
            report_results.append({
                "booking_idx": None,
                "attendance_file": report["attendance_file"],
                "meeting_title": report["meeting_title"],
                "meeting_start_time": report["meeting_start_time"],
                "matched": False,
            })
            continue

        booking_row = bookings_df.loc[best_idx]
        used_booking_ids.add(booking_row["Booking Id"])
        eval_result = evaluate_attendance_for_booking(report, booking_row)

        report_results.append({
            "booking_idx": best_idx,
            "attendance_file": report["attendance_file"],
            "meeting_title": report["meeting_title"],
            "meeting_start_time": report["meeting_start_time"],
            "matched": True,
            **eval_result,
        })

    report_results_df = pd.DataFrame(report_results)

    final_rows = []

    for idx, booking_row in bookings_df.iterrows():
        matched_report = report_results_df[report_results_df["booking_idx"] == idx]

        if not matched_report.empty:
            rr = matched_report.iloc[0]
            attendance_file_found = True
            customer_attended = bool(rr["customer_attended"])
            staff_attended = bool(rr["staff_attended"])
            customer_duration = rr["customer_duration_minutes"]
            staff_duration = rr["staff_duration_minutes"]
            matched_customer_participant = rr["matched_customer_participant"]
            matched_staff_participant = rr["matched_staff_participant"]
            attendance_file = rr["attendance_file"]
            meeting_title = rr["meeting_title"]
            participants_count = rr["participants_count"]
        else:
            attendance_file_found = False
            customer_attended = False
            staff_attended = False
            customer_duration = 0.0
            staff_duration = 0.0
            matched_customer_participant = ""
            matched_staff_participant = ""
            attendance_file = ""
            meeting_title = ""
            participants_count = 0

        status = build_status(customer_attended, staff_attended, attendance_file_found)

        final_rows.append({
            "Booking Id": booking_row.get("Booking Id", ""),
            "Booking DateTime": booking_row.get("booking_datetime", pd.NaT),
            "Customer Name": booking_row.get("Customer Name", ""),
            "Customer Email": booking_row.get("Customer Email", ""),
            "Staff Name": booking_row.get("Staff Name", ""),
            "Staff Email": booking_row.get("Staff Email", ""),
            "Service": booking_row.get("Service", ""),
            "Attendance File": attendance_file,
            "Meeting Title": meeting_title,
            "Attendance File Found": attendance_file_found,
            "Customer Attended": customer_attended,
            "Staff Attended": staff_attended,
            "Matched Customer Participant": matched_customer_participant,
            "Matched Staff Participant": matched_staff_participant,
            "Customer Duration Minutes": customer_duration,
            "Staff Duration Minutes": staff_duration,
            "Participants Count": participants_count,
            "Status": status,
            "Source": "Automated",
        })

    final_df = pd.DataFrame(final_rows)
    final_df = final_df.sort_values(by="Booking DateTime", ascending=True)
    final_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"[Auto] Merge complete: {OUTPUT_FILE}")
    return OUTPUT_FILE


# =========================
# MAIN
# =========================
def main():
    automation_step_1_bookings()
    automation_step_2_teams()
    automation_step_3_merge()
    print("[Auto] Full pipeline completed successfully.")


if __name__ == "__main__":
    main()