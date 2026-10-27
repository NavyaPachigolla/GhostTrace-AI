# Hacktoberfest Open-Source AI Challenge Week 4 Submission: "Ghost in the Machine"

## 👻 Project Title: GhostTrace AI

**Tagline:** A spooky, 100% local AI-powered computer activity storyteller.

- **Challenge:** Hacktoberfest Open-Source AI Challenge — Week 4: *Ghost in the Machine*
- **Primary AI Model:** `qwen2.5:3b` (Open-weight LLM running via Ollama)
- **User Interface:** Streamlit (Halloween Dark Cyberpunk Theme)
- **Repository URL:** `https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>` *(Placeholder: Insert your repository URL)*
- **Demo Video / Recording:** `https://www.youtube.com/watch?v=<YOUR_VIDEO_ID>` *(Placeholder: Insert your 60-90s recording link)*
- **Author:** `<YOUR_NAME_OR_HANDLE>`

---

## 🔮 1. Inspiration & The "Ghost in the Machine" Theme

Every developer and computer user has experienced that eerie feeling:
A computer fan roaring to life at 03:33 AM in an empty apartment, a strange disk activity LED blinking in a dark server closet, or a phantom network connection that leaves no audit trail.

For the **Week 4 "Ghost in the Machine"** challenge, **GhostTrace AI** takes this universal experience and turns it into an interactive paranormal investigation terminal. Instead of cold, sterile security alerts, GhostTrace AI reads simulated log files, detects mysterious anomalies with a transparent rule-based engine, and prompts a local open-weight AI model to transform the technical telemetry into an atmospheric, detective-style ghost story.

---

## 💻 2. What We Built

GhostTrace AI is a complete, modular, local Python application featuring:

1. **Haunted Activity Log Scanner:** A safe, read-only log parser supporting structured JSON and plain-text (`.log`, `.txt`) logs. It features strict path-traversal safeguards, file size limits, and malformed log tolerance.
2. **Rule-Based Mystery Detector:** A transparent heuristic engine that evaluates events for witching-hour occurrences (03:00–04:00 AM), phantom hardware IDs (`0xDEAD`, `0x0000NULL`), recurring authentication failures, and self-modifying file anomalies, assigning a deterministic mystery score from 0 to 100.
3. **Local AI Story Engine:** Harnesses **Qwen2.5 3B** locally through **Ollama** to craft atmospheric stories grounded in the exact timestamps and anomaly details. Supports 4 distinct styles:
   - *Haunted Computer*
   - *Digital Ghost Mystery*
   - *Abandoned Server Room*
   - *Retro Computer Horror*
4. **Resilient Offline Fallback:** If Ollama or the model is unavailable, GhostTrace automatically falls back to an internal procedural narrative engine, guaranteeing 100% reliability with zero crashes.
5. **Paranormal Investigation Timeline:** An interactive chronological visualizer with multi-criteria filtering by severity, category, keyword, and hour of day.
6. **5 Built-In Investigation Cases:** Instant 1-click cases (e.g. *The Midnight Process*, *The Forgotten Server*, *The File That Returned*) that require no file setup.

---

## 🧠 3. Why Local Open-Source AI?

A key philosophy of GhostTrace AI is **open innovation**:

- **Total Privacy:** System activity logs can contain sensitive contextual details. By running Qwen2.5 3B locally on Ollama, **zero data leaves the user's computer**. There are no cloud APIs, no external telemetry, and no privacy compromises.
- **Zero Cost & Free of API Keys:** Anyone with a personal computer can run GhostTrace AI immediately without paying for API tokens or managing expired keys.
- **Explainable AI:** The application makes a clear distinction between deterministic rule-based findings and creative AI interpretations. The user can inspect the exact heuristics that triggered the mystery score.
- **Offline Independence:** Whether you are on a plane or in an air-gapped environment, the app works seamlessly.

---

## 🚀 4. How to Run Locally

```powershell
# 1. Clone repository
git clone https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
cd ghosttrace-ai

# 2. Virtual environment setup
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Pull the local model in Ollama
ollama pull qwen2.5:3b

# 5. Run the Streamlit terminal
streamlit run app.py

# 6. Run automated test suite (25 tests)
python -m pytest -v
```

---

## 🧪 5. Testing & Verification

A comprehensive test suite of 25 automated tests covers:
- Safe handling of valid, empty, and malformed logs
- Rejection of unsupported extensions and path traversal exploits (`../../`)
- Mystery scoring heuristics and severity thresholds
- Multi-event pattern detection (simulated failed login bursts)
- Ollama API connection, prompt generation, and graceful offline fallback behavior
- Integrity of all built-in sample cases

---

## 📽️ 6. Screen Recording & Walkthrough

Refer to `DEMO_SCRIPT.md` for the step-by-step recording sequence highlighting:
1. Paranormal Investigation Dashboard metrics
2. Inspecting Case 001: The Midnight Process
3. Reviewing rule-based mystery scores and explanations
4. Exploring the Chronological Event Timeline
5. Generating a ghost story with Qwen2.5 3B / Fallback Engine in different narrative styles
