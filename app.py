from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="ChronoFocus Pro | Deep Work & Habit Studio",
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

# --- SIDEBAR: SETTINGS, LOGGER & BACKUPS ---
with st.sidebar:
    st.title("⏱️ ChronoFocus Pro")
    st.caption("Deep Work Timer, Soundscapes & Habit Studio")

    daily_goal = st.number_input(
        "Daily Focus Target (Minutes)",
        min_value=30,
        max_value=720,
        value=240,
        step=15,
    )

    st.divider()
    with st.form("log_session_form", clear_on_submit=True):
        st.subheader("➕ Log Focus Session")
        task_name = st.text_input("Task Name", placeholder="e.g., Ship v2.0 Upgrade")
        category = st.selectbox("Category", ("Deep Work", "Study", "Creative", "Fitness", "Planning"))
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
    st.subheader("💾 Backup & Restore")
    df_export = pd.DataFrame(st.session_state.sessions)
    st.download_button(
        label="⬇️ Export Focus Log (CSV)",
        data=df_export.to_csv(index=False).encode("utf-8"),
        file_name="chronofocus_backup.csv",
        mime="text/csv",
        use_container_width=True,
    )

    uploaded_csv = st.file_uploader("Restore from CSV Backup", type=("csv",))
    if uploaded_csv is not None:
        try:
            restored_df = pd.read_csv(uploaded_csv)
            required_cols = {"Task", "Category", "Minutes", "Timestamp"}
            if required_cols.issubset(set(restored_df.columns)):
                st.session_state.sessions = restored_df.to_dict(orient="records")
                st.success("Backup restored!")
            else:
                st.warning("CSV must contain Task, Category, Minutes, and Timestamp columns.")
        except Exception:
            st.warning("Could not read that CSV file.")

# --- MAIN HEADER & KPI METRICS ---
st.title("⏱️ ChronoFocus Pro: Deep Work & Habit Studio")
st.caption("Interactive Pomodoro timer with synthesized focus soundscapes, custom habit matrix & analytics")

df_sessions = pd.DataFrame(st.session_state.sessions)
total_mins = int(df_sessions["Minutes"].sum()) if not df_sessions.empty else 0
total_hours = total_mins / 60.0
session_count = len(df_sessions)
top_cat = df_sessions.groupby("Category")["Minutes"].sum().idxmax() if not df_sessions.empty else "None"
goal_pct = min(100, int((total_mins / daily_goal) * 100)) if daily_goal > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Focus Time", f"{total_mins} mins", f"{total_hours:.1f} hrs")
m2.metric("Completed Blocks", f"{session_count}")
m3.metric("Top Focus Area", top_cat)
m4.metric("Daily Goal Progress", f"{goal_pct}%", f"Target: {daily_goal}m")

tab_timer, tab_habits, tab_analytics = st.tabs(
    (
        "⏲️ Live Focus Timer & Soundscapes",
        "✅ Custom Habit Matrix",
        "📊 Time & Category Analytics",
    )
)

# ==============================================================================
# TAB 1: BROWSER POMODORO TIMER + SYNTHESIZED SOUNDSCAPES (JSON-INJECTED)
# ==============================================================================
with tab_timer:
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        preset_mins = st.selectbox(
            "Timer Preset",
            (25, 50, 90, 15, 5),
            format_func=lambda x: f"{x} Minutes ({'Break' if x <= 15 else 'Deep Focus'})",
        )
    with col_t2:
        soundscape = st.selectbox(
            "Focus Background Audio",
            ("Silent", "Deep Brown Noise", "Soft Rain Ambience", "40Hz Gamma Focus"),
        )
    with col_t3:
        st.write("")
        if st.button("⚡ Quick-Log This Preset Now", use_container_width=True):
            st.session_state.sessions.append(
                {
                    "Task": f"{preset_mins}-Min Focus Block",
                    "Category": "Deep Work" if preset_mins > 15 else "Planning",
                    "Minutes": int(preset_mins),
                    "Timestamp": datetime.now().strftime("%H:%M"),
                }
            )
            st.rerun()

    timer_cfg = json.dumps(
        {
            "minutes": preset_mins,
            "sound": soundscape,
        }
    )

    html_top = """
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
        body {
          background: #0e1117; color: #f8fafc;
          display: flex; flex-direction: column; align-items: center; justify-content: center;
          height: 290px; border: 1px solid #262730; border-radius: 16px; padding: 20px;
        }
        #status-badge {
          font-size: 12px; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase;
          color: #38bdf8; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3);
          padding: 4px 14px; border-radius: 20px; margin-bottom: 12px;
        }
        #clock {
          font-size: 80px; font-weight: 800; letter-spacing: 3px;
          color: #00e676; margin-bottom: 18px; line-height: 1;
        }
        .btns { display: flex; gap: 12px; }
        button {
          border: none; padding: 12px 26px; border-radius: 10px;
          font-size: 15px; font-weight: 700; cursor: pointer; transition: transform 0.1s;
        }
        button:active { transform: scale(0.96); }
        .start { background: #00e676; color: #052e16; }
        .pause { background: #f59e0b; color: #1c1917; }
        .reset { background: #334155; color: #f8fafc; }
      </style>
    </head>
    <body>
      <div id="status-badge">READY • SOUND: <span id="snd-label">SILENT</span></div>
      <div id="clock">25:00</div>
      <div class="btns">
        <button class="start" onclick="startTimer()">▶ Start Focus</button>
        <button class="pause" onclick="pauseTimer()">⏸ Pause</button>
        <button class="reset" onclick="resetTimer()">↺ Reset</button>
      </div>
      <script id="timer-cfg" type="application/json">"""

    html_bottom = """</script>
      <script>
        const CFG = JSON.parse(document.getElementById("timer-cfg").textContent);
        let totalSeconds = CFG.minutes * 60;
        let remaining = totalSeconds;
        let interval = null;
        let audioCtx = null;
        let ambientNode = null;

        document.getElementById("snd-label").innerText = CFG.sound.toUpperCase();

        function updateDisplay() {
          const m = String(Math.floor(remaining / 60)).padStart(2, "0");
          const s = String(remaining % 60).padStart(2, "0");
          document.getElementById("clock").innerText = m + ":" + s;
        }

        function startAmbient() {
          if (CFG.sound === "Silent" || ambientNode) return;
          try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === "suspended") audioCtx.resume();

            if (CFG.sound === "40Hz Gamma Focus") {
              const osc = audioCtx.createOscillator();
              const gain = audioCtx.createGain();
              osc.type = "sine";
              osc.frequency.value = 40;
              gain.gain.value = 0.08;
              osc.connect(gain).connect(audioCtx.destination);
              osc.start();
              ambientNode = osc;
            } else {
              const bufferSize = audioCtx.sampleRate * 2;
              const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
              const output = buffer.getChannelData(0);
              let lastOut = 0.0;
              for (let i = 0; i < bufferSize; i++) {
                const white = Math.random() * 2 - 1;
                if (CFG.sound === "Deep Brown Noise") {
                  output[i] = (lastOut + (0.02 * white)) / 1.02;
                  lastOut = output[i];
                  output[i] *= 2.5;
                } else {
                  output[i] = white * 0.25;
                }
              }
              const noise = audioCtx.createBufferSource();
              noise.buffer = buffer;
              noise.loop = true;

              const filter = audioCtx.createBiquadFilter();
              filter.type = "lowpass";
              filter.frequency.value = CFG.sound === "Deep Brown Noise" ? 320 : 950;

              const gain = audioCtx.createGain();
              gain.gain.value = 0.14;

              noise.connect(filter).connect(gain).connect(audioCtx.destination);
