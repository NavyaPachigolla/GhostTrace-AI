# GhostTrace AI 👻

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20Inference-black.svg)](https://ollama.com)
[![Model](https://img.shields.io/badge/LLM-Qwen2.5%203B-purple.svg)](https://ollama.com/library/qwen2.5)
[![Framework](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Hacktoberfest 2026](https://img.shields.io/badge/Hacktoberfest-Ghost%20in%20the%20Machine-orange.svg)](https://hacktoberfest.com/)

> **A spooky, 100% local AI-powered computer activity storyteller.**  
> Built for the **Hacktoberfest Open-Source AI Challenge Week 4: "Ghost in the Machine"**.

---

## ⚖️ Important Disclaimer

> [!NOTE]
> **GhostTrace AI is a fictional, paranormal-themed creative storytelling application.**  
> It inspects simulated sample computer logs and transforms anomalous patterns into entertaining detective-style ghost stories. It does **not** detect real ghosts, supernatural entities, or actual cyber security breaches. It does **not** access live OS system logs or collect private personal credentials.

---

## 📖 Overview

Have you ever heard your computer fans spin up violently at 03:33 AM? Or seen a blinking hard drive light in an empty, darkened room?

**GhostTrace AI** transforms everyday computer anomalies into eerie paranormal investigations. Users inspect fictional system events—such as unexpected midnight service restarts, simulated failed authentications, or phantom USB peripherals—and watch an open-weight local AI model (**Qwen2.5 3B via Ollama**) weave them into an atmospheric detective story.

### 🌟 Why Open Innovation & Local AI?

GhostTrace AI is engineered strictly for **on-device, open-source AI execution**:
1. **100% Local Privacy:** Your system logs and activity records never leave your machine. No telemetry, no cloud tokens, no third-party data collection.
2. **Deterministic Transparency:** The rule-based mystery detector scores anomalies through transparent, explainable heuristics before the LLM writes the story.
3. **Resilient Offline Operation:** If Ollama is offline or the model is not installed, the application seamlessly activates an **intelligent procedural narrative engine**, ensuring full functionality anywhere, anytime.

---

## 🔮 Core Features

| Feature | Description |
| :--- | :--- |
| **🔍 Haunted Log Scanner** | Safely ingests JSON and plain-text (`.log`, `.txt`) sample files with strict path-traversal guards and read-only guarantees. |
| **⚡ Mystery Detector** | Transparent rule engine calculating mystery scores (0–100) and flagging fictional anomalies (witching hour events, corrupted pointers, phantom hardware). |
| **📜 Local AI Storyteller** | Powered by Ollama + Qwen2.5 3B. Weaves real log evidence into atmospheric stories across 4 distinct styles. |
| **⏳ Paranormal Timeline** | Interactive chronological viewer with multi-criteria filtering by severity, event category, search keywords, and hour of day. |
| **📁 5 Built-in Cases** | Pre-packaged investigation cases ready to explore in 1 click without supplying external files. |
| **🛡️ Safe Offline Fallback** | Deterministic procedural narrative generator ready when Ollama is offline. |

---

## 🎭 Story Styles

GhostTrace AI adapts its narrative voice according to your chosen investigation flavor:

- **💻 Haunted Computer:** Flickering CRT phosphors, erratic cursor drifts, and whispers emanating from the motherboard instruction pipeline.
- **🕵️ Digital Ghost Mystery:** Noir cyber-investigation uncovering spectral footprints that defy network protocol logic.
- **🏢 Abandoned Server Room:** Subterranean data bunker dread, cold drafts near decommissioned racks, and lingering amber indicator diodes.
- **💾 Retro Computer Horror:** 1990s BBS lore, 14.4k dial-up static, amber monitor glare, and 3.5-inch floppy drive clicks.

---

## 📂 Built-in Investigation Cases

1. **Case 001: The Midnight Process**  
   *Spontaneous execution of unregistered `daemon.spirit` at 03:33:07 AM without parent PID, allocating 333 MB at `0xDEADBEEF`.*
2. **Case 002: The Forgotten Server**  
   *Telemetry heartbeats emitted from decommissioned node 13, accompanied by simulated failed logins from `guest_from_beyond` and a thermal plunge to 2.1°C.*
3. **Case 003: The File That Returned**  
   *Permanently erased archive `whispers_1999.bak` reappears in temporary storage, rewrites its own creation date backwards to 1999, and locks its handle.*
4. **Case 004: The Phantom Peripheral**  
   *Unregistered USB device `[VID:0x0000 PID:0xDEAD]` connects at 03:14 AM, rapidly injects keystrokes into the terminal, and vanishes.*
5. **Case 005: Haunted Syslog (Plain Text)**  
   *Demonstrates plain-text syslog file parsing, timestamp extraction, and pattern recognition.*

---

## 🏗️ Architecture & Pipeline

```text
       +------------------------------------+
       |  User / Sample Activity Logs       |
       |  (JSON, LOG, TXT Files)            |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |  ghosttrace.log_reader             |
       |  - Strict path sanitization        |
       |  - Read-only file guarantee        |
       |  - Malformed content resilience    |
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |  ghosttrace.mystery_detector       |
       |  - Witching hour detection         |
       |  - Keyword & pattern heuristics    |
       |  - Mystery score (0 - 100)         |
       |  - Explainable detection reasons   |
       +------------------------------------+
                         |
           +-------------+-------------+
           |                           |
           v                           v
+----------------------+   +-----------------------------+
| ghosttrace.timeline  |   | ghosttrace.story_engine     |
| - Severity filtering |   | - Ollama Client (Qwen2.5 3B)|
| - Event type queries |   | - Dynamic prompt grounding  |
| - Time window slices |   | - Procedural Fallback Engine|
+----------------------+   +-----------------------------+
           |                           |
           +-------------+-------------+
                         |
                         v
       +------------------------------------+
       |  Streamlit Paranormal UI (app.py)  |
       |  - Halloween dark cyberpunk theme  |
       |  - Live metrics & telemetry cards  |
       |  - Story exporter & regeneration   |
       +------------------------------------+
```

---

## ⚡ Quickstart Guide (Windows PowerShell)

Follow these exact steps in **Windows PowerShell** to set up and run GhostTrace AI:

### 1. Clone or Open the Repository
```powershell
cd c:\Users\SAMA\OneDrive\Desktop\week-5
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

> [!TIP]
> If PowerShell blocks script execution, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

### 3. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Setup Ollama and Download Qwen2.5 3B
If you haven't installed Ollama yet:
1. Download Ollama from [ollama.com](https://ollama.com).
2. Start Ollama:
```powershell
ollama serve
```
3. In another PowerShell window, pull the default lightweight open model:
```powershell
ollama pull qwen2.5:3b
```

> [!NOTE]
> If Ollama is not installed or running, GhostTrace AI will **automatically** use its built-in Offline Procedural Narrative Engine!

### 5. Launch the Streamlit Terminal
```powershell
streamlit run app.py
```
Open your browser to: **`http://localhost:8501`**

### 6. Run Automated Tests
```powershell
python -m pytest -v
```

---

## 🧪 Testing & Verification

The test suite covers edge cases, security validations, and offline behavior:

```powershell
python -m pytest -v
```

### Test Coverage Highlights:
- ✅ **Valid & Malformed Logs:** Safely parses standard JSON, single-line JSON, Syslog, and corrupt files without throwing unhandled exceptions.
- ✅ **Path Traversal Protection:** Rejects directory traversal attempts (`../../`) and restricts scans to safe boundaries.
- ✅ **Read-Only Guarantee:** Verifies that log files are never edited, moved, or deleted.
- ✅ **Mystery Scoring:** Validates witching hour scoring, keyword weighting, and burst pattern bonuses.
- ✅ **Graceful AI Fallback:** Tests that offline Ollama states or connection errors trigger the procedural fallback engine smoothly.
- ✅ **Case Integrity:** Verifies that all 5 sample cases exist, load cleanly, and produce flagged anomalies.

---

## ⚖️ Open-Source AI vs Closed Cloud APIs

| Aspect | GhostTrace AI (Local Open-Source AI) | Closed Hosted Cloud AI (e.g. Paid Cloud API) |
| :--- | :--- | :--- |
| **Data Privacy** | 🔒 **100% On-Device:** System logs remain strictly local. | ☁️ Logs and telemetry are transmitted to remote cloud servers. |
| **Cost** | 🆓 **Zero Cost:** Free open-weight models, no token fees. | 💳 **Pay-Per-Token:** Recurring billing and API key upkeep. |
| **Reliability** | ⚡ **Guaranteed Offline:** Operates in air-gapped environments. | ❌ **Cloud Dependency:** Fails when internet or servers go down. |
| **Inspectability** | 🔍 **Full Control:** Open weights, custom prompts, offline fallback. | 📦 **Black Box:** Unpredictable API model changes and deprecations. |
| **Hardware** | 💻 Requires 2–4 GB RAM / VRAM on local PC. | 📱 Offloads compute to vendor data centers. |

---

## 🛠️ Troubleshooting

- **Ollama connection fails or says "Offline":**
  - Verify that the Ollama service is running by opening `http://localhost:11434` in your browser or running `ollama list` in PowerShell.
  - If using a custom port, update the `Ollama Host URL` in the sidebar under **Advanced AI Settings**.
  - GhostTrace AI will automatically use the **Procedural Fallback Engine** so you can still use the app.
- **Model generation takes too long:**
  - On CPU-only setups, LLM inference may take 30–60 seconds. You can either:
    1. Select a lighter model or toggle **Force Offline Fallback Mode** in the sidebar for instantaneous story generation.
    2. Lower the temperature setting in the sidebar.
- **PowerShell Execution Policy Error:**
  - Run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

---

## 📁 Project Structure

```text
ghosttrace-ai/
├── app.py                     # Streamlit Paranormal Terminal Interface
├── requirements.txt           # Project dependencies
├── pyproject.toml             # Project metadata and pytest configuration
├── .gitignore                 # Version control ignores
├── .env.example               # Optional environment variables
├── README.md                  # Comprehensive project documentation
├── HACKTOBERFEST_POST.md      # Hacktoberfest submission deliverable
├── DEMO_SCRIPT.md             # 60-90 second demo recording walkthrough
├── ghosttrace/                # Core modular application package
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Constants, thresholds, and story styles
│   ├── log_reader.py          # Safe, read-only file scanner and parser
│   ├── mystery_detector.py    # Rule-based mystery scoring and heuristics
│   ├── story_engine.py        # Ollama Qwen2.5 3B client & procedural fallback
│   ├── timeline.py            # Event timeline filtering and stats
│   └── sample_cases.py        # Built-in case manager and metadata
├── sample_data/               # Sample log files
│   ├── midnight_process.json  # Case 001 sample log
│   ├── forgotten_server.json  # Case 002 sample log
│   ├── returning_file.json    # Case 003 sample log
│   ├── phantom_peripheral.json# Case 004 sample log
│   └── haunted_syslog.log     # Case 005 plain-text syslog
├── tests/                     # Automated test suite (25 tests)
│   ├── test_log_reader.py     # File parsing, safety & path tests
│   ├── test_mystery_detector.py # Heuristic rules & scoring tests
│   ├── test_story_engine.py   # Ollama & fallback story engine tests
│   └── test_sample_cases.py   # Sample case integrity & timeline tests
└── docs/
    └── screenshots/           # Demo screenshots placeholder
        └── README.md
```

---

## 📜 License

This project is licensed under the **MIT License**.
Built with 💜 for Hacktoberfest 2026.
