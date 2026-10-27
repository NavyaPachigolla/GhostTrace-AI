"""GhostTrace AI - Configuration and Constants.

Fictional paranormal-themed storytelling and log mystery detection configuration.
"""

from dataclasses import dataclass
from typing import Dict, List

# Core AI Settings
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:3b"
FALLBACK_MODEL = "qwen2.5:3b"
REQUEST_TIMEOUT_SECONDS = 120

# Allowed file extensions for safe scanning
SUPPORTED_EXTENSIONS = [".json", ".log", ".txt"]
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB limit per log file for safety

# Mystery Scoring Thresholds
SCORE_LOW_MAX = 30
SCORE_MEDIUM_MAX = 60
SCORE_HIGH_MAX = 80
SCORE_PARANORMAL_MAX = 100

# Story Styles
STORY_STYLES: Dict[str, Dict[str, str]] = {
    "haunted_computer": {
        "title": "Haunted Computer",
        "icon": "💻",
        "description": "Flickering phosphors, a cursor moving by itself, and whispers from the motherboard.",
        "tone": "Eerie, psychological, atmospheric, techno-chiller",
    },
    "digital_ghost": {
        "title": "Digital Ghost Mystery",
        "icon": "🕵️",
        "description": "A noir cyber-detective inspecting anomalies left by an entity that defies network logic.",
        "tone": "Noir detective, analytical suspense, cryptic cyber-investigation",
    },
    "abandoned_server": {
        "title": "Abandoned Server Room",
        "icon": "🏢",
        "description": "Cold draft in a subterranean data bunker where decommissioned racks still pulse with life.",
        "tone": "Claustrophobic, industrial gothic, ambient dread, forgotten machines",
    },
    "retro_horror": {
        "title": "Retro Computer Horror",
        "icon": "💾",
        "description": "Dial-up static, amber CRT glare, floppy disk clicks, and a 1990s BBS mystery.",
        "tone": "Analog horror, 90s tech lore, static distortion, nostalgic uncanny",
    },
}

# Paranormal Witching Hours (24-hour format)
WITCHING_HOUR_START = 3  # 03:00 AM
WITCHING_HOUR_END = 4    # 04:00 AM
MIDNIGHT_START = 0       # 00:00 AM
MIDNIGHT_END = 1         # 01:00 AM

# Keywords indicating fictional paranormal / mysterious patterns
MYSTERY_KEYWORDS: Dict[str, int] = {
    "phantom": 25,
    "daemon": 15,
    "whisper": 25,
    "shadow": 20,
    "0xdead": 30,
    "0x0000null": 30,
    "spectral": 30,
    "resurrect": 35,
    "witching": 35,
    "echo_": 25,
    "unknown device": 25,
    "unregistered": 20,
    "corrupt": 20,
    "ghost": 30,
    "void": 25,
    "null_ptr": 20,
    "entity": 25,
    "bypassed": 20,
    "manifest": 25,
    "spontaneous": 25,
    "poltergeist": 35,
}

# Legal & Ethics Disclaimer
APP_DISCLAIMER = (
    "GhostTrace AI is a fictional, paranormal-themed storytelling application built for "
    "entertainment and creative writing. It reads sample logs and does NOT detect real ghosts, "
    "supernatural occurrences, actual security vulnerabilities, or private system data."
)

PRIVACY_NOTICE = (
    "🔒 Privacy Notice: GhostTrace AI executes 100% locally on your machine. "
    "Sample log files are never sent over the internet or uploaded to any cloud server. "
    "When using local AI story generation, prompts are dispatched exclusively to your local "
    "Ollama instance (localhost:11434). No personal data or live system credentials are collected."
)
