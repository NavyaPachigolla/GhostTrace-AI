"""GhostTrace AI - Rule-Based Mystery Detector.

Transparent, deterministic scoring engine that evaluates sample events,
assigns mystery scores (0-100), tags fictional anomalies, and explains
the exact reasoning behind every flag.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ghosttrace.config import (
    MIDNIGHT_END,
    MIDNIGHT_START,
    MYSTERY_KEYWORDS,
    SCORE_HIGH_MAX,
    SCORE_LOW_MAX,
    SCORE_MEDIUM_MAX,
    WITCHING_HOUR_END,
    WITCHING_HOUR_START,
)
from ghosttrace.log_reader import LogEvent


@dataclass
class ScoredEvent:
    """A log event enriched with mystery scoring, classification, and reasoning."""
    event: LogEvent
    mystery_score: int
    severity: str  # "Low", "Medium", "High", "Paranormal"
    reasons: List[str] = field(default_factory=list)
    is_anomaly: bool = False
    classification: str = "Normal Event"  # "Normal Event" or "Fictional Anomaly"

    def to_dict(self) -> Dict:
        """Convert scored event to a dictionary representation."""
        return {
            "id": self.event.id,
            "timestamp": self.event.timestamp,
            "source": self.event.source,
            "event_type": self.event.event_type,
            "message": self.event.message,
            "mystery_score": self.mystery_score,
            "severity": self.severity,
            "reasons": self.reasons,
            "is_anomaly": self.is_anomaly,
            "classification": self.classification,
            "file_source": self.event.file_source,
            "details": self.event.details,
        }


@dataclass
class InvestigationSummary:
    """High-level metrics for an investigation case."""
    total_events: int = 0
    anomalies_detected: int = 0
    normal_events: int = 0
    peak_mystery_score: int = 0
    average_anomaly_score: float = 0.0
    threat_level: str = "Calm 🟢"
    top_anomalies: List[ScoredEvent] = field(default_factory=list)
    event_type_distribution: Dict[str, int] = field(default_factory=dict)


class MysteryDetector:
    """Evaluates sample log events against transparent rule sets."""

    def __init__(self, anomaly_threshold: int = 35):
        self.anomaly_threshold = anomaly_threshold

    def evaluate_event(self, event: LogEvent) -> ScoredEvent:
        """Score a single event and determine if it represents a fictional anomaly."""
        score = 0
        reasons: List[str] = []

        # 1. Witching Hour and Time-of-Day Rules
        time_score, time_reasons = self._check_time_anomaly(event)
        score += time_score
        reasons.extend(time_reasons)

        # 2. Keyword & Lexical Rules
        kw_score, kw_reasons = self._check_keywords(event)
        score += kw_score
        reasons.extend(kw_reasons)

        # 3. Behavioral Pattern Rules (Process, Auth, Device, FileSystem, Service)
        pattern_score, pattern_reasons = self._check_behavioral_patterns(event)
        score += pattern_score
        reasons.extend(pattern_reasons)

        # Clamp score to [0, 100]
        final_score = min(max(score, 0), 100)

        # Determine severity label
        severity = self._determine_severity(final_score)

        # Determine anomaly classification
        is_anomaly = final_score >= self.anomaly_threshold
        classification = "Fictional Anomaly" if is_anomaly else "Normal Event"

        if not reasons and not is_anomaly:
            reasons.append("Routine system activity within normal operating parameters.")

        return ScoredEvent(
            event=event,
            mystery_score=final_score,
            severity=severity,
            reasons=reasons,
            is_anomaly=is_anomaly,
            classification=classification,
        )

    def analyze_events(self, events: List[LogEvent]) -> Tuple[List[ScoredEvent], InvestigationSummary]:
        """Analyze a list of events and generate an aggregate investigation summary."""
        scored_events: List[ScoredEvent] = []
        if not events:
            return [], InvestigationSummary()

        # Step 1: Detect multi-event patterns (e.g. repeated failed logins)
        login_failure_counts: Dict[str, int] = {}
        for ev in events:
            if ev.event_type.lower() == "authentication" or "failed" in ev.message.lower():
                user_key = str(ev.details.get("user") or ev.source or "unknown")
                login_failure_counts[user_key] = login_failure_counts.get(user_key, 0) + 1

        # Step 2: Score each event individually with multi-event awareness
        total_score = 0
        anomalies: List[ScoredEvent] = []
        type_dist: Dict[str, int] = {}

        for ev in events:
            scored = self.evaluate_event(ev)

            # Boost if part of repeated simulated failed logins
            user_key = str(ev.details.get("user") or ev.source or "unknown")
            if login_failure_counts.get(user_key, 0) >= 3 and "failed" in ev.message.lower():
                repeat_boost = 20
                if "Repeated failed authentication burst detected." not in scored.reasons:
                    scored.mystery_score = min(100, scored.mystery_score + repeat_boost)
                    scored.reasons.append("Repeated failed authentication burst detected.")
                    scored.severity = self._determine_severity(scored.mystery_score)
                    scored.is_anomaly = scored.mystery_score >= self.anomaly_threshold
                    scored.classification = "Fictional Anomaly" if scored.is_anomaly else "Normal Event"

            scored_events.append(scored)

            type_dist[ev.event_type] = type_dist.get(ev.event_type, 0) + 1
            if scored.is_anomaly:
                anomalies.append(scored)
                total_score += scored.mystery_score

        # Step 3: Compute summary metrics
        total_events = len(scored_events)
        anomaly_count = len(anomalies)
        peak_score = max((s.mystery_score for s in scored_events), default=0)
        avg_score = (total_score / anomaly_count) if anomaly_count > 0 else 0.0

        threat_level = self._calculate_threat_level(peak_score, anomaly_count)
        top_anomalies = sorted(anomalies, key=lambda s: s.mystery_score, reverse=True)[:5]

        summary = InvestigationSummary(
            total_events=total_events,
            anomalies_detected=anomaly_count,
            normal_events=total_events - anomaly_count,
            peak_mystery_score=peak_score,
            average_anomaly_score=round(avg_score, 1),
            threat_level=threat_level,
            top_anomalies=top_anomalies,
            event_type_distribution=type_dist,
        )

        return scored_events, summary

    def _check_time_anomaly(self, event: LogEvent) -> Tuple[int, List[str]]:
        """Check for witching hour or abnormal night-time execution."""
        score = 0
        reasons: List[str] = []
        dt = event.parsed_time

        if dt is not None:
            hour = dt.hour
            minute = dt.minute

            if hour == WITCHING_HOUR_START:
                # 03:00 to 03:59 AM
                score += 35
                reasons.append(
                    f"Occurred during the Witching Hour ({hour:02d}:{minute:02d}) — peak paranormal window."
                )
            elif hour == MIDNIGHT_START:
                # 00:00 to 00:59 AM
                score += 20
                reasons.append(
                    f"Initiated at the stroke of midnight ({hour:02d}:{minute:02d})."
                )
            elif 1 <= hour < 5:
                # 01:00 to 04:59 AM
                score += 15
                reasons.append(
                    f"Triggered during nocturnal quiet hours ({hour:02d}:{minute:02d})."
                )

        return score, reasons

    def _check_keywords(self, event: LogEvent) -> Tuple[int, List[str]]:
        """Scan text fields for fictional paranormal / mystery keywords."""
        score = 0
        reasons: List[str] = []

        combined_text = f"{event.message} {event.source} {event.event_type} {str(event.details)}".lower()

        found_keywords: List[str] = []
        for kw, kw_weight in MYSTERY_KEYWORDS.items():
            if kw in combined_text:
                score += kw_weight
                found_keywords.append(kw)

        if found_keywords:
            sample_kws = ", ".join(f"'{k}'" for k in found_keywords[:3])
            reasons.append(f"Contains mysterious keyword signature: {sample_kws}.")

        return score, reasons

    def _check_behavioral_patterns(self, event: LogEvent) -> Tuple[int, List[str]]:
        """Check for domain-specific simulated anomalies."""
        score = 0
        reasons: List[str] = []
        msg = event.message.lower()
        etype = event.event_type.lower()
        details = {str(k).lower(): str(v).lower() for k, v in event.details.items()}

        # 1. Process Anomalies
        if etype == "process" or "process" in msg:
            if any(p in msg for p in ["daemon.spirit", "shadow_sync", "whisper_thread", "ghost_proc", "echo.exe"]):
                score += 30
                reasons.append("Unregistered background process executed without parent PID.")
            if "memory leak" in msg or "0xdeadbeef" in msg or "0x0000null" in msg:
                score += 25
                reasons.append("Corrupted pointer or paranormal memory address detected.")

        # 2. Device Anomalies
        if etype == "device" or "device" in msg or "usb" in msg:
            if "phantom" in msg or "unknown" in msg or "unregistered" in msg or "ghost" in msg:
                score += 30
                reasons.append("Unregistered phantom peripheral connected with invalid vendor handshake.")
            if "disconnect" in msg and "rapid" in msg:
                score += 20
                reasons.append("Rapid cyclic connection/disconnection cycle.")

        # 3. Authentication Anomalies
        if etype == "authentication" or "login" in msg or "auth" in msg:
            if any(u in msg for u in ["guest_from_beyond", "root_null", "shadow_admin", "user_unknown"]):
                score += 35
                reasons.append("Authentication attempted from non-existent phantom identity.")
            elif "failed" in msg:
                score += 15
                reasons.append("Simulated authentication failure.")

        # 4. FileSystem Anomalies
        if etype == "filesystem" or "file" in msg:
            if any(f in msg for f in [".wav", ".dat", ".tmp", "echo", "whispers", "dont_look_behind_you"]):
                score += 25
                reasons.append("Cryptic file manifestation in system storage.")
            if "resurrect" in msg or "returned" in msg or "reappeared" in msg:
                score += 35
                reasons.append("Deleted file reappeared with inverted creation timestamp.")

        # 5. Service Anomalies
        if etype == "service" or "daemon" in msg:
            if "unexpected restart" in msg or "spontaneous restart" in msg or "crashed" in msg:
                score += 25
                reasons.append("Service underwent unexpected spontaneous resurrection.")

        return score, reasons

    def _determine_severity(self, score: int) -> str:
        """Map score to human-readable severity level."""
        if score <= SCORE_LOW_MAX:
            return "Low"
        elif score <= SCORE_MEDIUM_MAX:
            return "Medium"
        elif score <= SCORE_HIGH_MAX:
            return "High"
        else:
            return "Paranormal"

    def _calculate_threat_level(self, peak_score: int, anomaly_count: int) -> str:
        """Synthesize an overall investigation threat level."""
        if anomaly_count == 0 or peak_score < 30:
            return "Calm 🟢"
        elif peak_score < 60:
            return "Elevated 🟡"
        elif peak_score < 80:
            return "Spooky 🟠"
        else:
            return "Paranormal Surge 🟣"
