"""GhostTrace AI - Story Engine.

Transforms scored log events into atmospheric, detective-style ghost stories
using either a local Ollama instance (Qwen2.5 3B) or an intelligent offline
procedural fallback generator.
"""

from dataclasses import dataclass
import json
import time
from typing import Dict, List, Optional, Tuple
import requests

from ghosttrace.config import (
    DEFAULT_MODEL,
    DEFAULT_OLLAMA_URL,
    REQUEST_TIMEOUT_SECONDS,
    STORY_STYLES,
)
from ghosttrace.mystery_detector import ScoredEvent


@dataclass
class StoryResult:
    """The outcome of a ghost story generation run."""
    text: str
    engine: str  # "Ollama (qwen2.5:3b)" or "GhostTrace Fallback Engine"
    style_key: str
    style_title: str
    model_name: str
    events_referenced: int
    duration_seconds: float
    is_fallback: bool


# Pre-crafted atmospheric narrative components for offline fallback
FALLBACK_NARRATIVES: Dict[str, Dict[str, str]] = {
    "haunted_computer": {
        "intro": (
            "The phosphors on the primary terminal began to hum with a discordant frequency "
            "long after the office lights had been turned off. Outside, the autumn rain slashed "
            "against the windowpanes, but inside the chassis, something colder than the storm was stirring."
        ),
        "climax": (
            "The cursor twitched—three pixels right, one pixel down—without anyone touching the mouse. "
            "A memory dump opened on its own, spitting hex addresses that spelled out fragmented pleas. "
            "Whatever inhabited the instruction pipeline didn't belong to the operating system."
        ),
        "ending": (
            "When the final event logged, the screen snapped to black. In the reflection of the glass, "
            "the chair behind the desk was empty—yet the terminal fan whined softly, breathing in sync with the room."
        ),
    },
    "digital_ghost": {
        "intro": (
            "Case file opened under dim fluorescent lights. In twenty years of digital forensics, "
            "I'd never seen an audit trail like this one. Clean signatures, zero brute-force noise—just "
            "a quiet, spectral presence gliding through memory buffers like smoke through an air vent."
        ),
        "climax": (
            "Every anomaly pointed back to a timestamp when no human hands were at the console. "
            "The network stack opened phantom sockets to addresses that haven't existed since the ARPANET era. "
            "It wasn't a hacker looking for financial records; it was something looking for a way out."
        ),
        "ending": (
            "I closed the investigation log, but the warning diode on the network card kept pulsing "
            "in steady three-beat rhythms: S-O-S in binary. Some digital ghosts refuse to be archived."
        ),
    },
    "abandoned_server": {
        "intro": (
            "Sub-basement Level 4. The server rack stood inside a cage of chain-link wire and dust. "
            "Decommissioned three winters ago, the cooling blowers should have been silent. "
            "Instead, a glacial draft rolled out from between the rack doors."
        ),
        "climax": (
            "Drive LEDs flickered in erratic, hypnotic waves. Telemetry showed temperature drops "
            "to near-freezing near CPU Core 0, while the rest of the chassis remained warm. "
            "A ghost process had taken root in the motherboard NVRAM, whispering commands to an empty room."
        ),
        "ending": (
            "I pulled the power cable. The amber power supply light faded—then slowly, impossibly, "
            "flickered back to life for one final second. The forgotten server was still listening."
        ),
    },
    "retro_horror": {
        "intro": (
            "It started with the sound of a 14.4k modem dialing in the dead silence of 03:00 AM. "
            "An amber CRT monitor cast long, jagged shadows across the wood-paneled walls. "
            "The date on the BIOS had rolled back decades."
        ),
        "climax": (
            "On the amber screen, line by line, characters appeared as if typed by invisible fingers: "
            "'PRESS ANY KEY TO RELEASE ME.' The 3.5-inch floppy drive clicked into gear with a wet, "
            "rhythmic metallic clatter that echoed through the empty hallway."
        ),
        "ending": (
            "The monitor flashed once with blinding phosphorus light, leaving an afterimage on my retinas "
            "of a face pressed against the inside of the glass. The modem line went dead, leaving only static."
        ),
    },
}


class GhostStoryEngine:
    """Manages AI-driven and fallback paranormal story generation."""

    def __init__(
        self,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        model_name: str = DEFAULT_MODEL,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

    def check_connection(self) -> Tuple[bool, List[str], str]:
        """Verify if Ollama is accessible and check downloaded models.

        Returns:
            (is_available, model_names, status_message)
        """
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                if self.model_name in models or any(self.model_name in m for m in models):
                    return True, models, f"Connected to Ollama. Model '{self.model_name}' is ready."
                else:
                    return (
                        True,
                        models,
                        f"Connected to Ollama, but '{self.model_name}' is not downloaded yet. (Available: {', '.join(models) if models else 'none'})",
                    )
            return False, [], f"Ollama returned HTTP status {resp.status_code}."
        except requests.exceptions.ConnectionError:
            return False, [], "Ollama is not running. Using local Fallback Story Engine."
        except requests.exceptions.Timeout:
            return False, [], "Ollama connection timed out. Using local Fallback Story Engine."
        except Exception as e:
            return False, [], f"Ollama connection error: {e}"

    def build_prompt(
        self,
        events: List[ScoredEvent],
        case_name: str,
        style_key: str,
        custom_instructions: str = "",
    ) -> Tuple[str, str]:
        """Construct system and user prompts grounded in specific flagged events."""
        style_info = STORY_STYLES.get(style_key, STORY_STYLES["haunted_computer"])

        system_prompt = (
            "You are an eerie paranormal investigation storyteller and atmospheric writer. "
            "Your task is to write a compelling, fictional short ghost story inspired by suspicious "
            "computer activity logs. Ground your story in the specific timestamps, process names, "
            "and anomalies provided. Maintain suspense, atmosphere, and the requested tone. "
            "Do NOT claim to detect real supernatural activity or real security breaches; frame this "
            "purely as creative, fictional storytelling."
        )

        # Extract top anomalies to feed into the prompt
        anomalies = [e for e in events if e.is_anomaly]
        if not anomalies:
            anomalies = events[:5]  # fallback if no anomalies flagged

        event_summaries = []
        for a in anomalies[:8]:
            event_summaries.append(
                f"- [{a.event.timestamp}] Source: {a.event.source} | Event: {a.event.event_type} | "
                f"Detail: {a.event.message} (Mystery Score: {a.mystery_score}/100, Reason: {'; '.join(a.reasons)})"
            )

        events_text = "\n".join(event_summaries)

        user_prompt = (
            f"Case File: {case_name}\n"
            f"Story Style: {style_info['title']} ({style_info['tone']})\n"
            f"Style Atmosphere: {style_info['description']}\n\n"
            f"Suspicious Log Events to Incorporate:\n"
            f"{events_text}\n\n"
            "Instructions:\n"
            "1. Write an atmospheric, spooky detective story (~300-450 words) exploring what happened.\n"
            "2. Naturally mention the key timestamps (like the witching hour), file/process names, and events.\n"
            "3. Build eerie tension leading to an unforgettable paranormal climax and chilling ending.\n"
        )

        if custom_instructions:
            user_prompt += f"Special User Note: {custom_instructions}\n"

        return system_prompt, user_prompt

    def generate_story(
        self,
        events: List[ScoredEvent],
        case_name: str,
        style_key: str = "haunted_computer",
        temperature: float = 0.7,
        custom_instructions: str = "",
        force_fallback: bool = False,
    ) -> StoryResult:
        """Generate a ghost story using Ollama or the local procedural fallback engine."""
        start_time = time.time()
        style_info = STORY_STYLES.get(style_key, STORY_STYLES["haunted_computer"])
        anomalies = [e for e in events if e.is_anomaly]
        ref_count = len(anomalies) if anomalies else len(events)

        if not force_fallback:
            # Check Ollama connection first
            is_connected, models, _ = self.check_connection()
            if is_connected:
                # Attempt live Ollama generation
                system_prompt, user_prompt = self.build_prompt(
                    events, case_name, style_key, custom_instructions
                )
                try:
                    payload = {
                        "model": self.model_name,
                        "system": system_prompt,
                        "prompt": user_prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "top_p": 0.9,
                            "num_predict": 380,
                        },
                    }
                    resp = requests.post(
                        f"{self.ollama_url}/api/generate",
                        json=payload,
                        timeout=self.timeout,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        generated_text = data.get("response", "").strip()
                        if generated_text:
                            elapsed = round(time.time() - start_time, 2)
                            return StoryResult(
                                text=generated_text,
                                engine=f"Ollama ({self.model_name})",
                                style_key=style_key,
                                style_title=style_info["title"],
                                model_name=self.model_name,
                                events_referenced=ref_count,
                                duration_seconds=elapsed,
                                is_fallback=False,
                            )
                except Exception:
                    # On any exception, seamlessly transition to fallback
                    pass

        # Fallback story generation
        fallback_text = self._generate_fallback_story(events, case_name, style_key)
        elapsed = round(time.time() - start_time, 2)

        return StoryResult(
            text=fallback_text,
            engine="GhostTrace Procedural Narrative Engine (Offline Fallback)",
            style_key=style_key,
            style_title=style_info["title"],
            model_name="Rule-Based Fallback",
            events_referenced=ref_count,
            duration_seconds=elapsed,
            is_fallback=True,
        )

    def _generate_fallback_story(
        self,
        events: List[ScoredEvent],
        case_name: str,
        style_key: str,
    ) -> str:
        """Construct an atmospheric story dynamically weaving the exact anomalies detected."""
        narrative = FALLBACK_NARRATIVES.get(style_key, FALLBACK_NARRATIVES["haunted_computer"])
        style_info = STORY_STYLES.get(style_key, STORY_STYLES["haunted_computer"])

        anomalies = [e for e in events if e.is_anomaly]
        if not anomalies:
            anomalies = events[:4]

        # Extract specific log breadcrumbs
        breadcrumbs = []
        for a in anomalies[:5]:
            ts = a.event.timestamp
            msg = a.event.message
            src = a.event.source
            score = a.mystery_score
            reason = a.reasons[0] if a.reasons else "Unknown occurrence"
            breadcrumbs.append(f"At {ts}, {src} logged an anomaly: '{msg}' (Mystery Score: {score}/100 — {reason}).")

        log_evidence = "\n".join(f"> 🕯️ {bc}" for bc in breadcrumbs)

        story_body = (
            f"### 📁 Case File: {case_name}\n"
            f"**Investigative Style:** {style_info['title']} | **Tone:** {style_info['tone']}\n\n"
            f"{narrative['intro']}\n\n"
            f"The digital forensic log captured an unmistakable sequence of anomalies:\n\n"
            f"{log_evidence}\n\n"
            f"{narrative['climax']}\n\n"
            f"The anomalies weren't random corruption. They formed a deliberate sequence—a digital breadcrumb trail "
            f"left behind by something that had learned to navigate the kernel while the human world slept. "
            f"Every thread, every unexpected service restart, resonated with the cold logic of an entity trying to speak.\n\n"
            f"{narrative['ending']}\n\n"
            f"---\n"
            f"*Generated by GhostTrace AI Offline Fallback Engine.*"
        )

        return story_body
