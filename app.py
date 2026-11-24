from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ChronoFocus | Deep Work & Habit Studio",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- INITIALIZE SESSION STATE SAFELY ---
if "sessions" not in st.session_state:
    st.session_state.sessions = [
        {"Task": "System Architecture & Coding", "Category": "Deep Work", "Minutes": 50, "Timestamp": "09:00"},
        {"Task": "Research & Documentation", "Category": "Study", "Minutes": 45, "Timestamp": "11:15"},
        {"Task": "Creative Design Sprint", "Category": "Creative", "Minutes": 30, "Timestamp": "14:00"},
    ]

if "habits" not in st.session_state:
    st.session_state.habits = {
        "Deep Work (90+ mins)": [True, True, True, False, True, True, False],
        "Daily Exercise / Movement": [True, False, True, True, True, False, True],
        "Zero Distraction Morning": [True, True, False, True, True, True, False],
        "Evening Review & Plan": [False, True, True, True, False, True, True],
    }

# --- SIDEBAR: QUICK SESSION LOGGER ---
with st.sidebar:
    st.title("⏱️ ChronoFocus")
    st.caption("Zero-Distraction Deep Work & Habit Tracker")

    with st.form("log_session_form", clear_on_submit=True):
        st.subheader("➕ Log Completed Focus Block")
        task_name = st.text_input("Task Name", placeholder="e.g., Build Python App")
        category = st.selectbox("Category", ["Deep Work", "Study", "Creative", "Fitness", "Planning"])
        duration = st.slider("Duration (Minutes)", min_value=5, max_value=180, value=25, step=5)
        submitted = st.form_submit_button("Save Focus Session", use_container_width=True)

        if submitted and task_name.strip():
            st.session_state.sessions.append(
                {
                    "Task": task_name.strip(),
                    "Category": category,
                    "Minutes": int(duration),
                    "Timestamp": datetime.now().strftime("%H:%M"),
                }
            )
            st.success("Session logged!")

    st.divider()
    df_export = pd.DataFrame(st.session_state.sessions)
    st.download_button(
        label="⬇️ Export Focus Log (CSV)",
        data=df_export.to_csv(index=False).encode("utf-8"),
        file_name="chronofocus_log.csv",
        mime="text/csv",
        use_container_width=True,
    )

# --- MAIN HEADER & TOP METRICS ---
st.title("⏱️ ChronoFocus: Deep Work & Habit Studio")
st.caption("Interactive Pomodoro countdown timer, weekly habit matrix & visual time analytics")

df_sessions = pd.DataFrame(st.session_state.sessions)
total_mins = int(df_sessions["Minutes"].sum())
total_hours = total_mins / 60.0
session_count = len(df_sessions)
top_cat = df_sessions.groupby("Category")["Minutes"].sum().idxmax()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Focus Time", f"{total_mins} mins", f"{total_hours:.1f} hrs")
m2.metric("Completed Blocks", f"{session_count}")
m3.metric("Top Focus Area", top_cat)
m4.metric("Daily Goal Progress", f"{min(100, int((total_mins / 240) * 100))}%", "Target: 240m")

tab_timer, tab_habits, tab_analytics = st.tabs(
    [
        "⏲️ Live Focus Timer",
        "✅ Weekly Habit Matrix",
        "📊 Time & Category Analytics",
    ]
)

# ==============================================================================
# TAB 1: SELF-CONTAINED BROWSER POMODORO TIMER
# ==============================================================================
with tab_timer:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        preset_mins = st.selectbox(
            "Timer Preset",
            (25, 50, 15, 5),
            format_func=lambda x: f"{x} Minutes ({'Break' if x <= 15 else 'Focus'})",
        )
    with col_t2:
        st.info("Click **Start** below. Plays a soft chime when the countdown finishes.")

    timer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body {{
          margin: 0; background: #0e1117; color: #f8fafc;
          font-family: system-ui, -apple-system, sans-serif;
          display: flex; flex-direction: column; align-items: center; justify-content: center;
          height: 260px; border: 1px solid #262730; border-radius: 16px;
        }}
        #clock {{
          font-size: 76px; font-weight: 800; letter-spacing: 3px;
          color: #00e676; margin-bottom: 18px;
        }}
        .btns {{ display: flex; gap: 12px; }}
        button {{
          border: none; padding: 12px 26px; border-radius: 10px;
          font-size: 16px; font-weight: 700; cursor: pointer;
        }}
        .start {{ background: #00e676; color: #052e16; }}
        .pause {{ background: #f59e0b; color: #1c1917; }}
        .reset {{ background: #334155; color: #f8fafc; }}
      </style>
    </head>
    <body>
      <div id="clock">{preset_mins:02d}:00</div>
      <div class="btns">
        <button class="start" onclick="startTimer()">▶ Start</button>
        <button class="pause" onclick="pauseTimer()">⏸ Pause</button>
        <button class="reset" onclick="resetTimer()">↺ Reset</button>
      </div>

      <script>
        let totalSeconds = {preset_mins} * 60;
        let remaining = totalSeconds;
        let interval = null;

        function updateDisplay() {{
          const m = String(Math.floor(remaining / 60)).padStart(2, "0");
          const s = String(remaining % 60).padStart(2, "0");
          document.getElementById("clock").innerText = m + ":" + s;
        }}

        function beep() {{
          try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            osc.type = "sine";
            osc.frequency.value = 528;
            osc.connect(ctx.destination);
            osc.start();
            setTimeout(() => osc.stop(), 400);
          }} catch (e) {{}}
        }}

        function startTimer() {{
          if (interval) return;
          interval = setInterval(() => {{
            if (remaining > 0) {{
              remaining--;
              updateDisplay();
            }} else {{
              clearInterval(interval);
              interval = null;
              beep();
            }}
          }}, 1000);
        }}

        function pauseTimer() {{
          clearInterval(interval);
          interval = null;
        }}

        function resetTimer() {{
          pauseTimer();
          remaining = totalSeconds;
          updateDisplay();
        }}
      </script>
    </body>
    </html>
    """
    components.html(timer_html, height=280, scrolling=False)

# ==============================================================================
# TAB 2: INTERACTIVE WEEKLY HABIT STREAK MATRIX
# ==============================================================================
with tab_habits:
    st.subheader("✅ 7-Day Consistency Matrix")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    habit_rows = []
    for habit_name, checks in st.session_state.habits.items():
        row_dict = {"Habit": habit_name}
        for idx, day_label in enumerate(days):
            row_dict[day_label] = checks[idx]
        habit_rows.append(row_dict)

    habit_df = pd.DataFrame(habit_rows)
    edited_df = st.data_editor(
        habit_df,
        use_container_width=True,
        hide_index=True,
        disabled=["Habit"],
    )

    for _, row in edited_df.iterrows():
        h_name = row["Habit"]
        st.session_state.habits[h_name] = [bool(row[d]) for d in days]

    total_checks = sum(sum(vals) for vals in st.session_state.habits.values())
    max_checks = len(st.session_state.habits) * 7
    consistency_pct = int((total_checks / max_checks) * 100) if max_checks else 0
    st.progress(consistency_pct / 100.0, text=f"Weekly Habit Consistency: {consistency_pct}% ({total_checks}/{max_checks} completed)")

# ==============================================================================
# TAB 3: TIME & CATEGORY ANALYTICS
# ==============================================================================
with tab_analytics:
    c1, c2 = st.columns(2)
    with c1:
        cat_summary = df_sessions.groupby("Category", as_index=False)["Minutes"].sum()
        fig_pie = px.pie(
            cat_summary,
            names="Category",
            values="Minutes",
            hole=0.45,
            template="plotly_dark",
            title="Time Distribution by Category",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        fig_bar = px.bar(
            df_sessions,
            x="Task",
            y="Minutes",
            color="Category",
            template="plotly_dark",
            title="Minutes per Focus Session",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("📋 Session History")
    st.dataframe(df_sessions, use_container_width=True, hide_index=True)
