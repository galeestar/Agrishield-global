from datetime import datetime
import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ChronoFocus | Command Center",
    page_icon="⚡",
    layout="wide",
)

# --- INITIALIZE SESSION STATE ---
if "sessions" not in st.session_state:
    st.session_state.sessions = [
        {"Task": "System Architecture & Coding", "Category": "Deep Work", "Minutes": 50, "Time": "09:00"},
        {"Task": "Research & Documentation", "Category": "Study", "Minutes": 45, "Time": "11:15"},
        {"Task": "Creative Design Sprint", "Category": "Creative", "Minutes": 30, "Time": "14:00"},
    ]

if "habits" not in st.session_state:
    st.session_state.habits = {
        "Deep Work (90+ mins)": [True, True, True, False, True, True, False],
        "Daily Exercise / Movement": [True, False, True, True, True, False, True],
        "Zero Distraction Morning": [True, True, False, True, True, True, False],
        "Evening Review & Plan": [False, True, True, True, False, True, True],
    }

# --- XP & LEVEL ENGINE ---
df_sessions = pd.DataFrame(st.session_state.sessions)
total_mins = int(df_sessions["Minutes"].sum()) if not df_sessions.empty else 0
xp_points = total_mins * 10
level = (xp_points // 500) + 1

if level >= 10:
    rank_title = "Grandmaster Architect"
elif level >= 6:
    rank_title = "Flow State Specialist"
elif level >= 3:
    rank_title = "Deep Focus Apprentice"
else:
    rank_title = "Focus Initiate"

# --- SIDEBAR: LOGGER & BACKUP ---
with st.sidebar:
    st.title("⚡ ChronoFocus")
    st.caption(f"Rank: **{rank_title}** (Level {level} • {xp_points:,} XP)")

    daily_goal = st.number_input("Daily Focus Goal (Minutes)", min_value=30, max_value=720, value=240, step=15)

    st.divider()
    with st.form("log_form", clear_on_submit=True):
        st.subheader("➕ Log Completed Session")
        task_name = st.text_input("Task Name", placeholder="e.g., Build App")
        category = st.selectbox("Category", ("Deep Work", "Study", "Creative", "Fitness", "Planning"))
        duration = st.slider("Duration (Minutes)", min_value=5, max_value=180, value=25, step=5)
        if st.form_submit_button("Save & Earn XP", use_container_width=True) and task_name.strip():
            st.session_state.sessions.append(
                {
                    "Task": task_name.strip(),
                    "Category": category,
                    "Minutes": int(duration),
                    "Time": datetime.now().strftime("%H:%M"),
                }
            )
            st.rerun()

    st.divider()
    if not df_sessions.empty:
        st.download_button(
            label="⬇️ Download Backup (CSV)",
            data=df_sessions.to_csv(index=False).encode("utf-8"),
            file_name="chronofocus_backup.csv",
            mime="text/csv",
            use_container_width=True,
        )

# --- MAIN DASHBOARD ---
st.title("⚡ ChronoFocus: Deep Work Command Center")
st.caption("Native focus timer, XP progression, habit tracker & time analytics")

total_hours = total_mins / 60.0
top_cat = df_sessions.groupby("Category")["Minutes"].sum().idxmax() if not df_sessions.empty else "None"
goal_pct = min(100, int((total_mins / daily_goal) * 100)) if daily_goal > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Focus", f"{total_mins} mins", f"{total_hours:.1f} hrs")
m2.metric("Current Level", f"Level {level}", f"{xp_points:,} XP")
m3.metric("Top Discipline", top_cat)
m4.metric("Daily Goal", f"{goal_pct}%", f"Target: {daily_goal}m")

tab_timer, tab_habits, tab_analytics = st.tabs(("⏲️ Focus Timer", "✅ Habit Matrix", "📊 Analytics"))

# --- TAB 1: PURE PYTHON NATIVE FOCUS TIMER ---
with tab_timer:
    c1, c2 = st.columns(2)
    with c1:
        preset_mins = st.selectbox("Select Session Length (Minutes)", (25, 50, 90, 15, 5))
    with c2:
        st.write("")
        if st.button("⚡ Instant-Log Preset (+XP)", use_container_width=True):
            st.session_state.sessions.append(
                {
                    "Task": f"{preset_mins}-Min Focus Sprint",
                    "Category": "Deep Work" if preset_mins > 15 else "Planning",
                    "Minutes": int(preset_mins),
                    "Time": datetime.now().strftime("%H:%M"),
                }
            )
            st.rerun()

    st.divider()
    timer_task = st.text_input("What are you focusing on right now?", value="Deep Work Session")

    if st.button("▶ Start Live Countdown", type="primary"):
        total_secs = int(preset_mins * 60)
        progress_bar = st.progress(0)
        clock_display = st.empty()

        for remaining in range(total_secs, -1, -1):
            mins, secs = divmod(remaining, 60)
            clock_display.markdown(f"## ⏳ `{mins:02d}:{secs:02d}` — **{timer_task}**")
            pct_done = int(((total_secs - remaining) / total_secs) * 100) if total_secs > 0 else 100
            progress_bar.progress(pct_done)
            time.sleep(1)

        st.balloons()
        st.success(f"🎉 Completed {preset_mins} minutes on '{timer_task}'!")
        st.session_state.sessions.append(
            {
                "Task": timer_task.strip() or "Focus Session",
                "Category": "Deep Work",
                "Minutes": int(preset_mins),
                "Time": datetime.now().strftime("%H:%M"),
            }
        )
        st.rerun()

# --- TAB 2: HABIT STREAK MATRIX ---
with tab_habits:
    st.subheader("✅ 7-Day Habit Consistency Matrix")

    with st.form("add_habit_form", clear_on_submit=True):
        new_habit = st.text_input("Create New Habit", placeholder="e.g., Read 20 Pages")
        if st.form_submit_button("➕ Add Habit") and new_habit.strip():
            clean_name = new_habit.strip()
            if clean_name not in st.session_state.habits:
                st.session_state.habits[clean_name] = [False, False, False, False, False, False, False]
                st.rerun()

    days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    rows = []
    for h_name, checks in st.session_state.habits.items():
        row_data = {"Habit": h_name}
        for i, day in enumerate(days):
            row_data[day] = checks[i]
        rows.append(row_data)

    edited_df = st.data_editor(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        disabled=("Habit",),
    )

    for _, row in edited_df.iterrows():
        st.session_state.habits[row["Habit"]] = [bool(row[d]) for d in days]

    done_count = sum(sum(v) for v in st.session_state.habits.values())
    max_count = len(st.session_state.habits) * 7
    pct = int((done_count / max_count) * 100) if max_count else 0
    st.progress(pct / 100.0, text=f"Weekly Consistency: {pct}% ({done_count}/{max_count} completed)")

# --- TAB 3: NATIVE CHARTS & LOG ---
with tab_analytics:
    if not df_sessions.empty:
        st.subheader("Minutes by Category")
        cat_chart_data = df_sessions.groupby("Category")["Minutes"].sum()
        st.bar_chart(cat_chart_data)

        st.subheader("📋 Session History")
        st.dataframe(df_sessions, use_container_width=True, hide_index=True)
    else:
        st.info("Log a focus session in the sidebar to see your analytics.")
