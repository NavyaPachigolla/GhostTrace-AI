"""GhostTrace AI 👻 - Paranormal Computer Activity Storyteller.

Hacktoberfest Open-Source AI Challenge Week 4: "Ghost in the Machine"
A spooky, local AI-powered computer activity storyteller that scans sample logs,
flags fictional anomalies with rule-based scoring, and weaves eerie detective stories.
"""

from datetime import datetime
import json
from pathlib import Path
import time
from typing import Dict, List, Optional
import streamlit as st

from ghosttrace.config import (
    APP_DISCLAIMER,
    DEFAULT_MODEL,
    DEFAULT_OLLAMA_URL,
    PRIVACY_NOTICE,
    STORY_STYLES,
)
from ghosttrace.log_reader import LogEvent, LogReader
from ghosttrace.mystery_detector import MysteryDetector, ScoredEvent
from ghosttrace.sample_cases import SAMPLE_CASES, SampleCaseManager
from ghosttrace.story_engine import GhostStoryEngine, StoryResult
from ghosttrace.timeline import InvestigationTimeline, TimelineFilter

# Streamlit Page Configuration
st.set_page_config(
    page_title="GhostTrace AI 👻 | Paranormal Activity Storyteller",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Halloween / Paranormal Dark Cyberpunk Styling
CUSTOM_CSS = """
<style>
/* Main Background & Fonts */
.stApp {
    background-color: #0c0d14;
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

/* Header & Glowing Title */
.ghost-header {
    background: linear-gradient(135deg, #161224 0%, #1f1435 50%, #2a1130 100%);
    border: 1px solid #7928ca44;
    box-shadow: 0 4px 25px rgba(121, 40, 202, 0.25);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.ghost-header::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #9d4edd, #ff7b00, #9d4edd);
}

.ghost-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #d8b4fe 0%, #ff9e00 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    display: inline-block;
}

.ghost-tagline {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 6px;
    font-weight: 400;
}

/* Metric Cards */
.metric-box {
    background: #141726;
    border: 1px solid #282d45;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-box:hover {
    transform: translateY(-2px);
    border-color: #7928ca;
}

.metric-num {
    font-size: 1.8rem;
    font-weight: 800;
    color: #f8fafc;
    font-family: 'Consolas', monospace;
}

.metric-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    margin-top: 4px;
}

/* Severity Badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-low {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-medium {
    background: rgba(234, 179, 8, 0.15);
    color: #facc15;
    border: 1px solid rgba(234, 179, 8, 0.3);
}

.badge-high {
    background: rgba(249, 115, 22, 0.15);
    color: #fb923c;
    border: 1px solid rgba(249, 115, 22, 0.3);
}

.badge-paranormal {
    background: rgba(168, 85, 247, 0.2);
    color: #c084fc;
    border: 1px solid rgba(168, 85, 247, 0.5);
    box-shadow: 0 0 10px rgba(168, 85, 247, 0.3);
}

/* Terminal & Log Viewer */
.terminal-window {
    background: #090a10;
    border: 1px solid #1f2438;
    border-radius: 8px;
    padding: 16px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.88rem;
    color: #cbd5e1;
    line-height: 1.5;
}

/* Story Output Dossier */
.story-dossier {
    background: #111320;
    border: 1px solid #3b2a54;
    border-left: 4px solid #a855f7;
    border-radius: 8px;
    padding: 24px;
    color: #e2e8f0;
    font-size: 1.05rem;
    line-height: 1.7;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #0f1019;
    border-right: 1px solid #1f2337;
}

/* Disclaimer Banner */
.disclaimer-banner {
    background: rgba(30, 27, 46, 0.8);
    border: 1px solid #4a3474;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #cbd5e1;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Session State
if "case_manager" not in st.session_state:
    st.session_state.case_manager = SampleCaseManager()
if "detector" not in st.session_state:
    st.session_state.detector = MysteryDetector()
if "generated_story" not in st.session_state:
    st.session_state.generated_story = None
if "active_case_id" not in st.session_state:
    st.session_state.active_case_id = "midnight_process"
if "ollama_url" not in st.session_state:
    st.session_state.ollama_url = DEFAULT_OLLAMA_URL
if "model_name" not in st.session_state:
    st.session_state.model_name = DEFAULT_MODEL


# Helper Functions
def get_severity_badge_html(severity: str) -> str:
    """Return styled HTML badge for severity."""
    css_class = f"badge-{severity.lower()}"
    return f'<span class="badge {css_class}">{severity}</span>'


def get_story_engine() -> GhostStoryEngine:
    return GhostStoryEngine(
        ollama_url=st.session_state.ollama_url,
        model_name=st.session_state.model_name,
    )


# Sidebar Setup
with st.sidebar:
    st.markdown("### 👻 GhostTrace Control")
    st.caption("Hacktoberfest AI Challenge: 'Ghost in the Machine'")

    # Case Selection Mode
    case_mode = st.radio(
        "Investigation Source",
        ["Built-in Sample Cases", "Upload Log File", "Custom Folder Scan"],
        index=0,
    )

    loaded_events: List[LogEvent] = []
    active_case_title = "Custom Case"
    active_case_desc = ""

    if case_mode == "Built-in Sample Cases":
        cases = st.session_state.case_manager.list_cases()
        case_options = {c.title: c.case_id for c in cases}
        selected_title = st.selectbox(
            "Select Paranormal Case",
            list(case_options.keys()),
            index=0,
        )
        selected_id = case_options[selected_title]
        st.session_state.active_case_id = selected_id
        case_obj = st.session_state.case_manager.get_case(selected_id)

        if case_obj:
            active_case_title = case_obj.title
            active_case_desc = case_obj.description
            loaded_events = st.session_state.case_manager.load_case_events(selected_id)
            st.info(f"**Difficulty:** {case_obj.difficulty}\n\n{case_obj.subtitle}")

    elif case_mode == "Upload Log File":
        uploaded_file = st.file_uploader(
            "Upload Sample Log (.json, .log, .txt)",
            type=["json", "log", "txt"],
            help="Upload a simulated log file. Only user-provided sample data is processed.",
        )
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8", errors="replace")
            from ghosttrace.log_reader import parse_json_content, parse_plaintext_content
            if uploaded_file.name.endswith(".json"):
                loaded_events = parse_json_content(content, uploaded_file.name)
            else:
                loaded_events = parse_plaintext_content(content, uploaded_file.name)
            active_case_title = f"Uploaded: {uploaded_file.name}"
            active_case_desc = f"Analyzing uploaded sample log containing {len(loaded_events)} events."
        else:
            st.warning("Please upload a sample log file to begin investigation.")

    elif case_mode == "Custom Folder Scan":
        folder_path_input = st.text_input(
            "Directory Path (Safe Demo Folder)",
            value=str(Path(__file__).resolve().parent / "sample_data"),
            help="Enter a directory containing sample .json, .log, or .txt files.",
        )
        if st.button("Scan Folder"):
            try:
                reader = LogReader()
                loaded_events = reader.scan_directory(Path(folder_path_input))
                active_case_title = f"Scanned: {Path(folder_path_input).name}"
                active_case_desc = f"Scanned folder with {len(loaded_events)} total events found."
                st.success(f"Loaded {len(loaded_events)} events from folder.")
            except Exception as e:
                st.error(f"Scan error: {e}")

    st.markdown("---")
    st.markdown("### 🧠 Local AI Model & Ollama")

    engine = get_story_engine()
    is_connected, available_models, status_msg = engine.check_connection()

    if is_connected:
        st.success(f"🟢 {status_msg}")
        if available_models:
            chosen_model = st.selectbox(
                "Ollama Model",
                available_models,
                index=available_models.index(st.session_state.model_name)
                if st.session_state.model_name in available_models
                else 0,
            )
            st.session_state.model_name = chosen_model
    else:
        st.warning(f"🟠 {status_msg}")
        st.caption("⚡ Offline Fallback Engine active. Prewritten procedural ghost stories will be generated.")

    with st.expander("⚙️ Advanced AI Settings"):
        st.session_state.ollama_url = st.text_input(
            "Ollama Host URL",
            value=st.session_state.ollama_url,
        )
        temperature = st.slider("Story Creativity (Temperature)", 0.2, 1.2, 0.75, 0.05)
        force_fallback_toggle = st.checkbox(
            "Force Offline Fallback Mode",
            value=False,
            help="Test the deterministic offline procedural narrative generator even when Ollama is running.",
        )

    st.markdown("---")
    st.markdown("### 🎭 Story Style")
    style_keys = list(STORY_STYLES.keys())
    style_choice = st.selectbox(
        "Narrative Flavor",
        style_keys,
        format_func=lambda k: f"{STORY_STYLES[k]['icon']} {STORY_STYLES[k]['title']}",
        index=0,
    )
    st.caption(f"_{STORY_STYLES[style_choice]['description']}_")

    st.markdown("---")
    st.caption("GhostTrace AI v1.0.0 • Local Open-Source AI")


# Header Banner
st.markdown(
    f"""
    <div class="ghost-header">
        <div class="ghost-title">GhostTrace AI 👻</div>
        <div class="ghost-tagline">
            Paranormal Investigation Terminal • Automated Mystery Detection & Local AI Storyteller
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Disclaimer & Privacy Notice Alert
st.markdown(
    f"""
    <div class="disclaimer-banner">
        <b>⚖️ Fictional Disclaimer:</b> {APP_DISCLAIMER}<br>
        <b>🔒 Local Privacy:</b> {PRIVACY_NOTICE}
    </div>
    """,
    unsafe_allow_html=True,
)

# Analyze Events with MysteryDetector
if not loaded_events:
    st.info("👈 Select a built-in sample case from the sidebar or upload a log file to begin.")
    st.stop()

scored_events, summary = st.session_state.detector.analyze_events(loaded_events)
timeline = InvestigationTimeline(scored_events)

# Dashboard Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-num">{summary.total_events}</div>
            <div class="metric-label">Events Analyzed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-num" style="color: #ff9e00;">{summary.anomalies_detected}</div>
            <div class="metric-label">Flagged Anomalies</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-num" style="color: #c084fc;">{summary.peak_mystery_score}/100</div>
            <div class="metric-label">Peak Mystery Score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-num" style="font-size: 1.3rem;">{summary.threat_level}</div>
            <div class="metric-label">Paranormal Threat Index</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab_scanner, tab_timeline, tab_story, tab_architecture = st.tabs([
    "🔍 Anomaly Scanner & Mystery Report",
    "⏳ Paranormal Investigation Timeline",
    "📜 Ghost Story Terminal",
    "🛡️ Safety, Privacy & Open AI",
])

# ==============================================================================
# TAB 1: Anomaly Scanner & Mystery Report
# ==============================================================================
with tab_scanner:
    st.markdown(f"### 📂 Investigation Dossier: {active_case_title}")
    if active_case_desc:
        st.markdown(f"> _{active_case_desc}_")

    c_filter, c_sort = st.columns([3, 1])
    with c_filter:
        show_anomalies_only = st.checkbox("Show Flagged Anomalies Only", value=True)
    with c_sort:
        search_query = st.text_input("Filter by keyword", "", placeholder="e.g. spirit, failed, 03:33...")

    display_events = scored_events
    if show_anomalies_only:
        display_events = [e for e in display_events if e.is_anomaly]
    if search_query:
        sq = search_query.lower()
        display_events = [
            e for e in display_events
            if sq in e.event.message.lower()
            or sq in e.event.source.lower()
            or any(sq in r.lower() for r in e.reasons)
        ]

    st.caption(f"Displaying {len(display_events)} of {summary.total_events} events")

    for se in display_events:
        border_color = (
            "#a855f7" if se.severity == "Paranormal"
            else "#fb923c" if se.severity == "High"
            else "#facc15" if se.severity == "Medium"
            else "#22c55e"
        )
        anomaly_icon = "👻" if se.is_anomaly else "📋"

        with st.container():
            st.markdown(
                f"""
                <div style="background: #121422; border-left: 4px solid {border_color}; border-radius: 8px; padding: 14px; margin-bottom: 12px; border: 1px solid #1f2438;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div>
                            <b>{anomaly_icon} {se.event.timestamp}</b> &nbsp;|&nbsp; 
                            <span style="color: #94a3b8;">Source: <code>{se.event.source}</code></span> &nbsp;|&nbsp;
                            <span style="color: #94a3b8;">Type: <code>{se.event.event_type}</code></span>
                        </div>
                        <div>
                            {get_severity_badge_html(se.severity)}
                            <span style="font-weight: 700; color: {border_color}; margin-left: 8px; font-family: monospace;">Score: {se.mystery_score}/100</span>
                        </div>
                    </div>
                    <div style="font-size: 0.95rem; color: #f1f5f9; margin-bottom: 8px;">
                        <b>Message:</b> {se.event.message}
                    </div>
                    <div style="background: #0a0b12; padding: 8px 12px; border-radius: 6px; font-size: 0.85rem; color: #cbd5e1;">
                        <b>Rule Findings:</b> {' • '.join(se.reasons)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Metadata details dropdown
            if se.event.details:
                with st.expander(f"Inspect Raw Telemetry [{se.event.id}]"):
                    st.json(se.event.details)


# ==============================================================================
# TAB 2: Paranormal Investigation Timeline
# ==============================================================================
with tab_timeline:
    st.markdown("### ⏳ Chronological Event Flow")
    st.caption("Explore how suspicious activity unfolded over time.")

    # Timeline Controls
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        sel_severities = st.multiselect(
            "Filter Severities",
            ["Paranormal", "High", "Medium", "Low"],
            default=["Paranormal", "High", "Medium", "Low"],
        )
    with t_col2:
        available_types = timeline.get_available_event_types()
        sel_types = st.multiselect(
            "Filter Event Types",
            available_types,
            default=available_types,
        )
    with t_col3:
        hour_range = st.slider("Filter Hour of Day (00:00 - 23:00)", 0, 23, (0, 23))

    timeline_filter = TimelineFilter(
        severities=set(sel_severities) if sel_severities else None,
        event_types=set(sel_types) if sel_types else None,
        start_hour=hour_range[0],
        end_hour=hour_range[1],
    )
    timeline_events = timeline.filter_events(timeline_filter)

    st.markdown("---")
    if not timeline_events:
        st.warning("No events match the selected timeline filters.")
    else:
        for idx, te in enumerate(timeline_events, start=1):
            sev_badge = get_severity_badge_html(te.severity)
            time_display = te.event.timestamp
            icon = "🔮" if te.severity == "Paranormal" else "⚡" if te.is_anomaly else "🕒"

            col_time, col_card = st.columns([1, 4])
            with col_time:
                st.markdown(f"**{icon} {time_display}**")
                st.caption(f"Step #{idx:02d}")
            with col_card:
                with st.expander(f"{te.event.source} — {te.event.message[:65]}...", expanded=(te.severity in ["Paranormal", "High"])):
                    st.markdown(f"**Event Type:** `{te.event.event_type}`")
                    st.markdown(f"**Message:** {te.event.message}")
                    st.markdown(f"**Mystery Score:** `{te.mystery_score}/100` &nbsp; {sev_badge}", unsafe_allow_html=True)
                    st.markdown(f"**Classification:** `{te.classification}`")
                    st.markdown("**Rule Detections:**")
                    for r in te.reasons:
                        st.markdown(f"- 🕯️ {r}")
                    if te.event.details:
                        st.markdown("**Attached Metadata:**")
                        st.json(te.event.details)


# ==============================================================================
# TAB 3: Ghost Story Terminal
# ==============================================================================
with tab_story:
    st.markdown("### 📜 Paranormal Storyteller Terminal")
    st.caption("Transforms flagged computer anomalies into atmospheric detective fiction using local AI.")

    s_col1, s_col2 = st.columns([3, 1])
    with s_col1:
        custom_notes = st.text_input(
            "Investigator's Notebook / Story Guidance (Optional)",
            placeholder="e.g. Focus on the cold draft in the server room, make the narrator a tired nighttime security guard...",
        )
    with s_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        gen_clicked = st.button("🕯️ Generate Story", type="primary", use_container_width=True)

    if gen_clicked:
        with st.spinner("Channeling the digital ghost... summoning local narrative engine..."):
            story_engine = get_story_engine()
            res = story_engine.generate_story(
                events=scored_events,
                case_name=active_case_title,
                style_key=style_choice,
                temperature=temperature,
                custom_instructions=custom_notes,
                force_fallback=force_fallback_toggle,
            )
            st.session_state.generated_story = res

    current_story: Optional[StoryResult] = st.session_state.generated_story

    if current_story:
        # Display Story Details Header
        status_color = "#facc15" if current_story.is_fallback else "#4ade80"
        engine_badge = f'<span style="background: rgba(0,0,0,0.4); border: 1px solid {status_color}; color: {status_color}; padding: 4px 10px; border-radius: 6px; font-size: 0.82rem;">⚙️ Engine: {current_story.engine}</span>'

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; margin-bottom: 12px;">
                <div>
                    <b>Style:</b> {current_story.style_title} &nbsp;|&nbsp; 
                    <b>Events Referenced:</b> {current_story.events_referenced} &nbsp;|&nbsp;
                    <b>Generation Time:</b> {current_story.duration_seconds}s
                </div>
                <div>{engine_badge}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Dossier Container
        st.markdown(
            f"""
            <div class="story-dossier">
                {current_story.text.replace(chr(10), '<br>')}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        action_c1, action_c2, _ = st.columns([1, 1, 2])
        with action_c1:
            st.download_button(
                "💾 Save Story (.txt)",
                data=current_story.text,
                file_name=f"ghosttrace_story_{st.session_state.active_case_id}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with action_c2:
            if st.button("🔄 Regenerate", use_container_width=True):
                with st.spinner("Regenerating with alternative narrative variations..."):
                    story_engine = get_story_engine()
                    res = story_engine.generate_story(
                        events=scored_events,
                        case_name=active_case_title,
                        style_key=style_choice,
                        temperature=temperature,
                        custom_instructions=custom_notes,
                        force_fallback=force_fallback_toggle,
                    )
                    st.session_state.generated_story = res
                    st.rerun()

    else:
        st.markdown(
            """
            <div style="background: #111322; border: 1px dashed #343b59; border-radius: 8px; padding: 40px; text-align: center; color: #94a3b8;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">🕯️</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #cbd5e1;">No Story Generated Yet</div>
                <div style="font-size: 0.9rem; margin-top: 6px;">
                    Click the <b>🕯️ Generate Story</b> button above to weave the detected anomalies into a ghost story.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# TAB 4: Safety, Privacy & Open AI
# ==============================================================================
with tab_architecture:
    st.markdown("### 🛡️ Safety, Local AI & Architectural Integrity")

    st.markdown(
        """
        GhostTrace AI was engineered specifically for the **Hacktoberfest Open-Source AI Challenge Week 4: "Ghost in the Machine"**.
        It places local privacy, explainability, and user safety at the center of AI-driven creative tools.
        """
    )

    col_sec1, col_sec2 = st.columns(2)

    with col_sec1:
        st.markdown("#### 🔒 Strict Privacy & Non-Invasive Scanning")
        st.markdown(
            """
            - **No Whole-Computer Scans:** The log reader scans **only** files in the user-selected folder or built-in sample cases.
            - **Zero Modification Guarantee:** Log files are opened strictly in read-only mode (`r`, UTF-8). GhostTrace never writes, edits, moves, or deletes original files.
            - **Path Traversal Protection:** Directory traversal attacks (`../`) are detected and blocked via `sanitize_path()`.
            - **No Cloud Uploads:** No user telemetry or logs leave your machine.
            - **Local Inference:** When Ollama is used, inference requests are sent solely to `http://localhost:11434`.
            """
        )

        st.markdown("#### ⚖️ Responsible & Ethical Framing")
        st.markdown(
            """
            - **Purely Fictional Storytelling:** GhostTrace AI explicitly discloses that it generates fictional creative stories.
            - **No False Breach Claims:** Rule detections clearly state that findings are simulated anomalies, not real cyber breaches or genuine supernatural events.
            - **Transparent Scoring:** Every single mystery point is explained with an explicit deterministic rule.
            """
        )

    with col_sec2:
        st.markdown("#### 💡 Open-Source AI vs Closed Cloud APIs")
        st.markdown(
            """
            | Dimension | Local Open AI (Ollama + Qwen2.5 3B) | Closed Hosted Cloud API |
            | :--- | :--- | :--- |
            | **Privacy** | 🔒 100% On-Device (No data egress) | ☁️ Logs sent to third-party cloud |
            | **Cost** | 🆓 Free, zero API token costs | 💳 Pay-per-token recurring fees |
            | **Offline Utility** | ⚡ Works without internet connection | ❌ Breaks on disconnect or downtime |
            | **Transparency** | 🔍 Open weights & inspectable prompts | 📦 Black box hosted model |
            | **Hardware** | 💻 Requires 2-4 GB RAM / VRAM | 📱 Runs on thin client / web |
            """
        )

        st.markdown("#### ⚙️ Graceful Degradation Design")
        st.markdown(
            """
            If Ollama is stopped, offline, or the Qwen2.5 3B model is not yet pulled,
            GhostTrace AI does not crash. It automatically engages the **GhostTrace Procedural Narrative Engine**,
            synthesizing dynamic ghost stories based on the exact detected timestamps and anomalies.
            """
        )

    st.markdown("---")
    st.markdown("#### 🏗️ Architecture Pipeline")
    st.code(
        """
   +----------------------+      +----------------------+
   | Sample Log Files     | ---> | Safe LogReader       |
   | (JSON / LOG / TXT)   |      | (Path & Type Guard)  |
   +----------------------+      +----------------------+
                                            |
                                            v
                                 +----------------------+
                                 | Mystery Detector     |
                                 | (Deterministic Rules)|
                                 +----------------------+
                                            |
                       +--------------------+--------------------+
                       |                                         |
                       v                                         v
            +----------------------+                  +----------------------+
            | Timeline Manager     |                  | Local GhostStory     |
            | (Filter, Sort, View) |                  | Engine (Qwen2.5 3B)  |
            +----------------------+                  +----------------------+
                       |                                         |
                       +--------------------+--------------------+
                                            |
                                            v
                               +-------------------------+
                               | Streamlit Paranormal UI |
                               +-------------------------+
        """,
        language="text",
    )
