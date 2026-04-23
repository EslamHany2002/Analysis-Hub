"""
Instructor Scheduler Page - Full Original Version
3 Tabs: Instructors, Weekly View, Assign New Groups
"""

import streamlit as st
import pandas as pd

from data.scheduler_data import load_schedule_excel, recompute, fmt_time, intervals_overlap
from data.schedule_storage import save_schedule_json, load_schedule_json
from config.themes import T
from config.constants import ALL_DAYS, TRACK_COLORS
from ui.components import (
    render_page_header,
    show_info_box,
    card_metric,
)


def render_scheduler():
    """Render the full Instructor Scheduler dashboard."""
    render_page_header(
        "Instructor Schedule Dashboard",
        "View schedules, detect conflicts, and assign new groups.",
        "🎓"
    )

    # ══════════════════════════════════════════════════════════════════
    # LOAD DATA
    # ══════════════════════════════════════════════════════════════════
    if not st.session_state.get("scheduler_file_loaded", False):
        existing_data = load_schedule_json()
        if existing_data:
            st.session_state.scheduler_instructors = existing_data
            st.session_state.scheduler_file_loaded = True

    uploaded = st.file_uploader("Upload Excel Schedule", type=["xlsx"], key="sched_upload")

    if "scheduler_instructors" not in st.session_state:
        st.session_state.scheduler_instructors = load_schedule_json() or {}
        st.session_state.scheduler_file_loaded = bool(st.session_state.scheduler_instructors)

    if uploaded is not None:
        excel_bytes = uploaded.read()
        st.session_state.scheduler_instructors = load_schedule_excel(excel_bytes)
        save_schedule_json(st.session_state.scheduler_instructors)
        st.session_state.scheduler_file_loaded = True

    if not st.session_state.scheduler_file_loaded:
        show_info_box(
            "Upload an Excel file containing a <b>Summary</b> sheet with columns "
            "<b>Track</b>, <b>Instructor</b>, <b>Group</b>, <b>Day</b>, <b>From</b>, and <b>To</b>.",
            "info"
        )
        return

    insts = st.session_state.scheduler_instructors
    all_tracks = sorted(set(d["track"] for d in insts.values())) if insts else []
    total_groups = sum(len(d["unique_groups"]) for d in insts.values()) if insts else 0

    # ══════════════════════════════════════════════════════════════════
    # KPI CARDS
    # ══════════════════════════════════════════════════════════════════
    c1, c2, c3 = st.columns(3)
    card_metric(c1, len(insts), "Instructors", T["accent"])
    card_metric(c2, total_groups, "Groups", T["green"])
    card_metric(c3, len(all_tracks), "Tracks", T["amber"])

    # ══════════════════════════════════════════════════════════════════
    # FILTERS
    # ══════════════════════════════════════════════════════════════════
    f1, f2, f3 = st.columns(3)
    sel_track = f1.selectbox("Track", ["All Tracks"] + all_tracks, key="sched_track")
    sel_day = f2.selectbox("Working Day", ["All Days"] + ALL_DAYS, key="sched_day")
    search = f3.text_input("Search instructor", key="sched_search")

    # ══════════════════════════════════════════════════════════════════
    # TABS
    # ══════════════════════════════════════════════════════════════════
    tab1, tab2, tab3 = st.tabs([
        "  📋  Instructors  ",
        "  📅  Weekly View  ",
        "  🔄  Assign New Groups  ",
    ])

    # ══════════════════════════════════════════════════════════════════
    # TAB 1: Instructors
    # ══════════════════════════════════════════════════════════════════
    with tab1:
        filtered = {
            n: d for n, d in insts.items()
            if (sel_track == "All Tracks" or d["track"] == sel_track)
            and (sel_day == "All Days" or sel_day in d["busy_days"])
            and (not search or search.lower() in n.lower())
        }

        if not filtered:
            st.info("No instructors match the current filters.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Shown", len(filtered))
            m2.metric("Total Groups", sum(len(d["unique_groups"]) for d in filtered.values()))
            avg = sum(len(d["unique_groups"]) for d in filtered.values()) / max(len(filtered), 1)
            m3.metric("Avg Groups / Instructor", f"{avg:.1f}")
            m4.metric("Tracks", len(set(d["track"] for d in filtered.values())))

            st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)

            # ── Add New Instructor ──
            with st.expander("➕  Add New Instructor"):
                anc1, anc2 = st.columns(2)
                new_name = anc1.text_input("Instructor Name", key="new_inst_name", placeholder="e.g. Ahmed Ali")
                track_options = sorted(TRACK_COLORS.keys()) or ["General"]
                new_track = anc2.selectbox("Track", track_options, key="new_inst_track")
                if st.button("Add Instructor", key="add_inst_btn"):
                    nm = new_name.strip()
                    if nm and nm not in insts:
                        insts[nm] = recompute({"track": new_track, "groups": []})
                        st.session_state.scheduler_instructors = insts
                        save_schedule_json(st.session_state.scheduler_instructors)
                        st.success(f"✅ Added {nm}")
                        st.rerun()
                    elif nm in insts:
                        st.warning("Instructor already exists.")
                    else:
                        st.warning("Please enter a name.")

            st.markdown("<div style='margin:6px 0'></div>", unsafe_allow_html=True)

            # ── Instructor Cards ──
            cols3 = st.columns(3)
            for idx, (name, data) in enumerate(sorted(filtered.items())):
                track = data["track"]
                tc = TRACK_COLORS.get(track, "#6b7280")
                groups = data["unique_groups"]
                off = data["off_days"]
                busy = data["busy_days"]

                with cols3[idx % 3]:
                    groups_html = ""
                    for gname, sessions in list(groups.items()):
                        days_parts = " · ".join(
                            f"{s['day'][:3]} {fmt_time(s['from'])}–{fmt_time(s['to'])}"
                            for s in sessions
                        )
                        groups_html += f"""
                        <div style="display:flex;align-items:flex-start;gap:8px;padding:6px 0;border-bottom:1px solid {T['border']}">
                          <div style="width:5px;height:5px;border-radius:50%;background:{tc};flex-shrink:0;margin-top:6px"></div>
                          <div>
                            <div style="font-size:0.8rem;color:{T['text']};font-weight:500;font-family:'DM Mono',monospace;line-height:1.3">{gname}</div>
                            <div style="font-size:0.68rem;color:{T['muted']};margin-top:2px">{days_parts}</div>
                          </div>
                        </div>"""
                    if not groups_html:
                        groups_html = f"<div style='font-size:0.76rem;color:{T['muted']};padding:6px 0'>No groups assigned</div>"

                    off_html = "".join(
                        f'<span style="background:{T["offbg"]};border:1px solid {T["offborder"]};color:{T["offtext"]};border-radius:6px;padding:3px 9px;font-size:0.7rem;margin:2px;display:inline-block">{d}</span>'
                        for d in off
                    ) or f"<span style='color:{T['muted']};font-size:0.74rem'>No off days</span>"

                    busy_html = "".join(
                        f'<span style="background:{tc}22;border:1px solid {tc}55;color:{tc};border-radius:6px;padding:3px 9px;font-size:0.7rem;margin:2px;display:inline-block">{d}</span>'
                        for d in busy
                    ) or f"<span style='color:{T['muted']};font-size:0.74rem'>No working days</span>"

                    st.markdown(f"""
                    <div style="background:{T['surface']};border:1px solid {T['border']};border-radius:14px;padding:18px 20px;border-top:3px solid {tc}">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
                        <div>
                          <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:{T['text']};line-height:1.2">{name}</div>
                          <span style="background:{tc}22;color:{tc};border:1px solid {tc}55;border-radius:20px;padding:2px 10px;font-size:0.68rem;font-family:'DM Mono',monospace;margin-top:4px;display:inline-block">
                            {track}
                          </span>
                        </div>
                        <div style="text-align:right">
                          <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:{tc}">{len(groups)}</div>
                          <div style="font-size:0.62rem;color:{T['muted']};text-transform:uppercase;letter-spacing:0.08em">groups</div>
                        </div>
                      </div>

                      <div style="font-size:0.64rem;color:{T['muted']};text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px">Working Days</div>
                      <div style="margin-bottom:10px">{busy_html}</div>

                      <div style="font-size:0.64rem;color:{T['muted']};text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px">Groups & Schedule</div>
                      <div style="margin-bottom:10px">{groups_html}</div>

                      <div style="font-size:0.64rem;color:{T['muted']};text-transform:uppercase;letter-spacing:0.1em;margin-bottom:5px">Off Days</div>
                      <div>{off_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Edit Instructor ──
                    with st.expander(f"✏️  Edit — {name}"):
                        rows_edit = [
                            {"Group": g["group"], "Day": g["day"], "From": g["from"], "To": g["to"]}
                            for g in data["groups"]
                        ]
                        df_edit = pd.DataFrame(rows_edit) if rows_edit else pd.DataFrame(columns=["Group", "Day", "From", "To"])

                        edited_df = st.data_editor(
                            df_edit,
                            num_rows="dynamic",
                            use_container_width=True,
                            key=f"de_{name}",
                            column_config={
                                "Day": st.column_config.SelectboxColumn("Day", options=ALL_DAYS),
                                "From": st.column_config.TextColumn("From (HH:MM:SS)"),
                                "To": st.column_config.TextColumn("To   (HH:MM:SS)"),
                            },
                        )

                        st.markdown("<div style='margin:8px 0 4px'></div>", unsafe_allow_html=True)
                        track_options = sorted(TRACK_COLORS.keys()) or [track]
                        idx_track = track_options.index(track) if track in track_options else 0
                        new_track_sel = st.selectbox("Change Track", track_options, index=idx_track, key=f"tr_{name}")

                        eb1, eb2 = st.columns(2)
                        if eb1.button("💾 Save Changes", key=f"save_{name}", use_container_width=True):
                            new_groups = []
                            for _, row in edited_df.iterrows():
                                if pd.notna(row["Group"]) and str(row["Group"]).strip():
                                    new_groups.append({
                                        "group": str(row["Group"]).strip(),
                                        "day": str(row["Day"]).strip(),
                                        "from": str(row["From"]).strip(),
                                        "to": str(row["To"]).strip(),
                                    })
                            data["groups"] = new_groups
                            data["track"] = new_track_sel
                            st.session_state.scheduler_instructors[name] = recompute(data)
                            save_schedule_json(st.session_state.scheduler_instructors)
                            st.success("✅ Saved!")
                            st.rerun()

                        if eb2.button("🗑️ Delete Instructor", key=f"del_{name}", use_container_width=True):
                            del st.session_state.scheduler_instructors[name]
                            save_schedule_json(st.session_state.scheduler_instructors)
                            st.warning(f"Deleted {name}")
                            st.rerun()

                    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 2: Weekly View
    # ══════════════════════════════════════════════════════════════════
    with tab2:
        wc1, wc2 = st.columns([2, 1])
        wv_track = wc1.selectbox("Track", ["All Tracks"] + sorted(set(d["track"] for d in insts.values())), key="wv_track")
        wv_search = wc2.text_input("Search instructor", key="wv_search")

        filtered_wv = {
            n: d for n, d in insts.items()
            if (wv_track == "All Tracks" or d["track"] == wv_track)
            and (not wv_search or wv_search.lower() in n.lower())
        }

        st.markdown("<div style='margin:10px 0'></div>", unsafe_allow_html=True)
        day_cols = st.columns(7)

        for ci, day in enumerate(ALL_DAYS):
            day_entries = []
            for iname, idata in sorted(filtered_wv.items()):
                sessions_today = [g for g in idata["groups"] if g["day"] == day]
                if sessions_today:
                    day_entries.append({"name": iname, "track": idata["track"], "sessions": sessions_today})

            day_cols[ci].markdown(f"""
            <div style="background:{T['surface']};border:1px solid {T['border']};border-radius:10px 10px 0 0;padding:10px;text-align:center;border-bottom:2px solid {T['accent']}">
              <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.85rem;color:{T['text']}">{day}</div>
              <div style="font-size:0.64rem;color:{T['muted']};margin-top:2px">{len(day_entries)} instructor{'s' if len(day_entries) != 1 else ''}</div>
            </div>
            """, unsafe_allow_html=True)

            if not day_entries:
                day_cols[ci].markdown(f"""
                <div style="background:{T['surface2']};border:1px solid {T['border']};border-radius:0 0 8px 8px;padding:18px 10px;text-align:center;color:{T['muted']};font-size:0.74rem">No sessions</div>
                """, unsafe_allow_html=True)
                continue

            for entry in day_entries:
                itc = TRACK_COLORS.get(entry["track"], "#6b7280")
                sess_html = ""
                for idx, s in enumerate(entry["sessions"]):
                    border_style = f"border-bottom:1px solid {T['border']};" if idx < len(entry["sessions"]) - 1 else ""
                    sess_html += (
                        f'<div style="padding:4px 0;{border_style}">'
                        f'<div style="font-size:0.72rem;color:{T["text"]};line-height:1.3;font-family:\'DM Mono\',monospace">{s["group"]}</div>'
                        f'<div style="font-size:0.64rem;color:{T["muted"]};margin-top:1px">{fmt_time(s["from"])} – {fmt_time(s["to"])}</div>'
                        f'</div>'
                    )

                day_cols[ci].markdown(f"""
                <div style="background:{T['surface2']};border:1px solid {T['border']};border-radius:0 0 8px 8px;padding:10px;margin-bottom:4px;border-left:3px solid {itc};border-top:none">
                  <div style="font-size:0.74rem;font-weight:700;color:{itc};font-family:'Syne',sans-serif;margin-bottom:6px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="{entry['name']}">{entry['name']}</div>
                  {sess_html}
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # TAB 3: Assign New Groups
    # ══════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown(f"""
        <div style="background:{T['surface']};border:1px solid {T['border']};border-radius:12px;padding:16px 20px;margin-bottom:20px">
          <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:{T['text']};margin-bottom:4px">🔄 Assign New Groups to Instructors</div>
          <div style="font-size:0.8rem;color:{T['muted']}">
            Enter new groups manually or upload a file. The system checks for exact time-slot conflicts before suggesting available instructors.
          </div>
        </div>
        """, unsafe_allow_html=True)

        all_tracks_list = sorted(set(d["track"] for d in insts.values()))
        if not all_tracks_list:
            st.info("No instructors loaded.")
            return
        target_track = st.selectbox("🎯 Target Track", all_tracks_list, key="assign_track")
        st.markdown("---")

        method = st.radio("Input Method", ["📝 Manual Entry", "📁 Upload File"], horizontal=True, key="assign_method")
        new_groups_list = []

        if method == "📝 Manual Entry":
            num = st.number_input("Number of groups", 1, 15, 2, key="assign_num")
            for i in range(int(num)):
                st.markdown(
                    f'<div style="font-size:0.74rem;color:{T["accent2"]};font-family:Syne,sans-serif;'
                    f'font-weight:700;margin:10px 0 4px">Group {i+1}</div>',
                    unsafe_allow_html=True
                )
                gc1, gc2, gc3, gc4 = st.columns([2, 2, 1, 1])
                gn = gc1.text_input("Group name", key=f"an_{i}", placeholder="e.g. AI Online 99")
                gd = gc2.multiselect("Days", key=f"ad_{i}", options=ALL_DAYS)
                gf = gc3.text_input("From", key=f"af_{i}", placeholder="14:00:00")
                gt = gc4.text_input("To", key=f"at_{i}", placeholder="17:00:00")
                if gn and gd:
                    new_groups_list.append({"name": gn, "days": gd, "from": gf or "00:00:00", "to": gt or "23:59:00"})
        else:
            nf = st.file_uploader("Upload groups file (.xlsx)", type=["xlsx"], key="assign_file")
            if nf:
                try:
                    xf2 = pd.ExcelFile(nf)
                    s2 = st.selectbox("Sheet", xf2.sheet_names, key="assign_sheet")
                    df2 = xf2.parse(s2)
                    st.dataframe(df2.head(10), use_container_width=True)
                    cl = {str(c).lower().strip(): c for c in df2.columns}
                    nc = next((cl[c] for c in cl if "group" in c or "name" in c), df2.columns[0])
                    dc = next((cl[c] for c in cl if "day" in c), None)
                    fc = next((cl[c] for c in cl if "from" in c or "start" in c), None)
                    ec = next((cl[c] for c in cl if c == "to" or "end" in c), None)
                    for _, row in df2.iterrows():
                        gn = str(row.get(nc, "")).strip()
                        if not gn or gn.lower() == "nan":
                            continue
                        raw_d = str(row.get(dc, "")) if dc else ""
                        gd = [x.strip().capitalize() for x in raw_d.replace(",", " ").split() if x.strip().capitalize() in ALL_DAYS]
                        gf = str(row.get(fc, "00:00:00")) if fc else "00:00:00"
                        gt = str(row.get(ec, "23:59:00")) if ec else "23:59:00"
                        if gd:
                            new_groups_list.append({"name": gn, "days": gd, "from": gf, "to": gt})
                except Exception as e:
                    st.error(f"Error reading file: {e}")

        st.markdown("<div style='margin:8px 0'></div>", unsafe_allow_html=True)

        # ── Find Available ──
        if new_groups_list and st.button("🔍 Find Available Instructors", type="primary", key="assign_run"):
            pool = {n: d for n, d in insts.items() if d["track"] == target_track}
            if not pool:
                st.warning(f"No instructors in track: {target_track}")
            else:
                st.markdown("---")
                st.markdown(
                    f'<div style="font-family:Syne,sans-serif;font-size:1.05rem;font-weight:700;'
                    f'color:{T["text"]};margin-bottom:14px">Results — {target_track}</div>',
                    unsafe_allow_html=True
                )

                for grp in new_groups_list:
                    available = []
                    conflicted = []
                    for iname, idata in pool.items():
                        conf = []
                        for day in grp["days"]:
                            for s in [g for g in idata["groups"] if g["day"] == day]:
                                if intervals_overlap(grp["from"], grp["to"], s["from"], s["to"]):
                                    conf.append(f"{day}: {s['group']} ({fmt_time(s['from'])}–{fmt_time(s['to'])})")
                        if conf:
                            conflicted.append({"name": iname, "conflicts": conf})
                        else:
                            available.append(iname)

                    days_str = " · ".join(grp["days"])
                    time_str = f"{fmt_time(grp['from'])} – {fmt_time(grp['to'])}"
                    col_edge = T["green"] if available else T["red"]
                    icon = "✅" if available else "❌"

                    st.markdown(f"""
                    <div style="background:{T['surface']};border:1px solid {T['border']};border-left:4px solid {col_edge};border-radius:12px;padding:18px 20px;margin-bottom:14px">
                      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                        <div>
                          <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;color:{T['text']}">{icon} {grp['name']}</div>
                          <div style="font-size:0.76rem;color:{T['muted']};margin-top:3px">📅 {days_str} &nbsp;|&nbsp; 🕐 {time_str}</div>
                        </div>
                        <div style="text-align:right">
                          <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;color:{col_edge}">{len(available)}</div>
                          <div style="font-size:0.62rem;color:{T['muted']};text-transform:uppercase">available</div>
                        </div>
                      </div>
                    """, unsafe_allow_html=True)

                    if available:
                        st.markdown(
                            f'<div style="font-size:0.68rem;color:{T["muted"]};text-transform:uppercase;'
                            f'letter-spacing:0.08em;margin-bottom:8px">Available Instructors</div>',
                            unsafe_allow_html=True
                        )
                        avail_html = "".join(
                            f'<span style="background:{T["green"]}18;border:1px solid {T["green"]}66;'
                            f'color:{T["green"]};border-radius:8px;padding:5px 14px;font-size:0.78rem;'
                            f'margin:3px;display:inline-block;font-family:DM Mono, monospace">✓ {a}</span>'
                            for a in available
                        )
                        st.markdown(f"<div style='margin-bottom:8px'>{avail_html}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f"<div style='color:{T['red']};font-size:0.82rem;margin-bottom:8px'>"
                            f"No fully available instructors for this slot.</div>",
                            unsafe_allow_html=True
                        )

                    if conflicted:
                        with st.expander(f"View conflicts ({len(conflicted)})", expanded=False):
                            for item in conflicted:
                                st.markdown(f"**{item['name']}**")
                                for conflict in item["conflicts"]:
                                    st.markdown(f"- {conflict}")

                    st.markdown("</div>", unsafe_allow_html=True)