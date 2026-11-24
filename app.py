from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ChronoFocus v3.0 | Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- SAFE SESSION STATE INITIALIZATION ---
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

# --- XP & RANK ENGINE ---
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

# --- SIDEBAR: COMMAND DECK, LOGGER & BACKUPS ---
with st.sidebar:
    st.title("⚡ ChronoFocus v3.0")
    st.caption(f"Rank: **{rank_title}** (Lvl {level} • {xp_points:,} XP)")

    daily_goal = st.number_input(
        "Daily Focus Target (Minutes)",
        min_value=30,
        max_value=720,
        value=240,
        step=15,
    )

    st.divider()
    with st.form("log_session_form", clear_on_submit=True):
        st.subheader("➕ Log Completed Session")
        task_name = st.text_input("Task Name", placeholder="e.g., Build Feature v3")
        category = st.selectbox("Category", ("Deep Work", "Study", "Creative", "Fitness", "Planning"))
        duration = st.slider("Duration (Minutes)", min_value=5, max_value=180, value=25, step=5)
        submitted = st.form_submit_button("Save & Earn XP", use_container_width=True)

        if submitted and task_name.strip():
            st.session_state.sessions.append(
                {
                    "Task": task_name.strip(),
                    "Category": category,
                    "Minutes": int(duration),
                    "Timestamp": datetime.now().strftime("%H:%M"),
                }
            )
            st.rerun()

    st.divider()
    st.subheader("💾 Data Vault")
    if not df_sessions.empty:
        st.download_button(
            label="⬇️ Download Backup (CSV)",
            data=df_sessions.to_csv(index=False).encode("utf-8"),
            file_name="chronofocus_v3_backup.csv",
            mime="text/csv",
            use_container_width=True,
        )

    uploaded_csv = st.file_uploader("Restore CSV Backup", type=("csv",))
    if uploaded_csv is not None:
        try:
            restored_df = pd.read_csv(uploaded_csv)
            required_cols = {"Task", "Category", "Minutes", "Timestamp"}
            if required_cols.issubset(set(restored_df.columns)):
                st.session_state.sessions = restored_df.to_dict(orient="records")
                st.success("Sessions restored!")
        except Exception:
            st.warning("Could not read CSV file.")

# --- TOP HUD & KPI METRICS ---
st.title("⚡ ChronoFocus v3.0: Deep Work Command Center")
st.caption("Animated neon focus timer, 3-layer soundscape mixer, habit matrix & XP progression")

total_hours = total_mins / 60.0
session_count = len(df_sessions)
top_cat = df_sessions.groupby("Category")["Minutes"].sum().idxmax() if not df_sessions.empty else "None"
goal_pct = min(100, int((total_mins / daily_goal) * 100)) if daily_goal > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Focus Time", f"{total_mins} mins", f"{total_hours:.1f} hrs")
m2.metric("Focus Level", f"Lvl {level}", f"{xp_points:,} XP")
m3.metric("Top Discipline", top_cat)
m4.metric("Daily Target", f"{goal_pct}%", f"Goal: {daily_goal}m")

tab_timer, tab_habits, tab_analytics = st.tabs(
    (
        "⏲️ Hyper-Timer & Sound Mixer",
        "✅ Habit Streak Matrix",
        "📊 Performance Telemetry",
    )
)

# ==============================================================================
# TAB 1: ANIMATED RADIAL RING TIMER + 3-LAYER AMBIENT AUDIO MIXER
# ==============================================================================
with tab_timer:
    c_top1, c_top2 = st.columns((2, 1))
    with c_top1:
        preset_mins = st.selectbox(
            "Select Focus Block",
            (25, 50, 90, 15, 5),
            format_func=lambda x: f"{x} Minutes ({'Recharge Break' if x <= 15 else 'Deep Focus Sprint'})",
        )
    with c_top2:
        st.write("")
        if st.button("⚡ Quick-Log Preset (+XP)", use_container_width=True):
            st.session_state.sessions.append(
                {
                    "Task": f"{preset_mins}-Min Focus Sprint",
                    "Category": "Deep Work" if preset_mins > 15 else "Planning",
                    "Minutes": int(preset_mins),
                    "Timestamp": datetime.now().strftime("%H:%M"),
                }
            )
            st.rerun()

    timer_payload = json.dumps({"minutes": preset_mins})

    html_part_1 = """
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
        body {
          background: radial-gradient(circle at top, #131b2e 0%, #090d16 100%);
          color: #f8fafc; border: 1px solid #26324b; border-radius: 18px;
          padding: 24px; display: flex; flex-direction: column; align-items: center;
          justify-content: space-between; height: 420px; user-select: none;
        }
        .ring-wrap {
          position: relative; width: 210px; height: 210px;
          display: flex; align-items: center; justify-content: center;
        }
        svg { transform: rotate(-90deg); width: 210px; height: 210px; }
        circle { fill: none; stroke-width: 10; }
        .bg-ring { stroke: #1e293b; }
        .prog-ring {
          stroke: #00e676; stroke-linecap: round;
          stroke-dasharray: 597; stroke-dashoffset: 0;
          transition: stroke-dashoffset 0.5s linear, stroke 0.3s;
        }
        #clock {
          position: absolute; font-size: 46px; font-weight: 800; letter-spacing: 2px; color: #f8fafc;
        }
        .controls { display: flex; gap: 12px; }
        button {
          border: none; padding: 11px 24px; border-radius: 10px;
          font-size: 14px; font-weight: 800; cursor: pointer; transition: transform 0.1s;
        }
        button:active { transform: scale(0.96); }
        .btn-start { background: #00e676; color: #052e16; box-shadow: 0 0 18px rgba(0, 230, 118, 0.35); }
        .btn-pause { background: #f59e0b; color: #1c1917; }
        .btn-reset { background: #334155; color: #f8fafc; }
        .mixer {
          width: 100%; max-width: 680px; background: rgba(15, 23, 42, 0.85);
          border: 1px solid #1e293b; border-radius: 14px; padding: 14px 20px;
          display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
        }
        .channel { display: flex; flex-direction: column; gap: 6px; font-size: 12px; font-weight: 700; color: #94a3b8; }
        input[type="range"] { width: 100%; accent-color: #38bdf8; cursor: pointer; }
      </style>
    </head>
    <body>
      <div class="ring-wrap">
        <svg viewBox="0 0 210 210">
          <circle class="bg-ring" cx="105" cy="105" r="95"></circle>
          <circle id="progress-circle" class="prog-ring" cx="105" cy="105" r="95"></circle>
        </svg>
        <div id="clock">25:00</div>
      </div>

      <div class="controls">
        <button class="btn-start" onclick="startTimer()">▶ Start Focus</button>
        <button class="btn-pause" onclick="pauseTimer()">⏸ Pause</button>
        <button class="btn-reset" onclick="resetTimer()">↺ Reset</button>
      </div>

      <div class="mixer">
        <div class="channel">
          <span>🌊 Deep Brown Noise</span>
          <input type="range" id="vol-brown" min="0" max="100" value="0" oninput="updateMixer()">
        </div>
        <div class="channel">
          <span>🌧️ Soft Rain Ambience</span>
          <input type="range" id="vol-rain" min="0" max="100" value="0" oninput="updateMixer()">
        </div>
        <div class="channel">
          <span>🧠 40Hz Gamma Focus</span>
          <input type="range" id="vol-gamma" min="0" max="100" value="0" oninput="updateMixer()">
        </div>
      </div>

      <script id="timer-data" type="application/json">"""

    html_part_2 = """</script>
      <script>
        const CFG = JSON.parse(document.getElementById("timer-data").textContent);
        const CIRCUMFERENCE = 597;
        let totalSeconds = CFG.minutes * 60;
        let remaining = totalSeconds;
        let timerId = null;

        let audioCtx = null;
        let brownGain = null;
        let rainGain = null;
        let gammaGain = null;

        function ensureAudio() {
          if (audioCtx) {
            if (audioCtx.state === "suspended") audioCtx.resume();
            return;
          }
          audioCtx = new (window.AudioContext || window.webkitAudioContext)();

          // 1. Brown Noise Generator
          const bufSize = audioCtx.sampleRate * 2;
          const brownBuf = audioCtx.createBuffer(1, bufSize, audioCtx.sampleRate);
          const bOut = brownBuf.getChannelData(0);
          let last = 0.0;
          for (let i = 0; i < bufSize; i++) {
