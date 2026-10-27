"""Tests for MysteryDetector, rule scoring, severity thresholds, and anomaly detection."""

from datetime import datetime
import pytest

from ghosttrace.log_reader import LogEvent
from ghosttrace.mystery_detector import MysteryDetector


@pytest.fixture
def detector():
    return MysteryDetector(anomaly_threshold=35)


def test_normal_event_low_score(detector: MysteryDetector):
    """Verify routine, daytime system operations receive low scores and are classified as normal."""
    event = LogEvent(
        id="norm_1",
        timestamp="2026-10-31 14:30:00",
        source="SystemKernel",
        event_type="Process",
        message="Standard update service completed successfully.",
        parsed_time=datetime(2026, 10, 31, 14, 30, 0),
    )
    scored = detector.evaluate_event(event)
    assert scored.mystery_score <= 30
    assert scored.severity == "Low"
    assert not scored.is_anomaly
    assert scored.classification == "Normal Event"
    assert any("Routine system activity" in r for r in scored.reasons)


def test_witching_hour_scoring(detector: MysteryDetector):
    """Verify events occurring during 03:00-04:00 AM receive high witching hour bonus."""
    event = LogEvent(
        id="witch_1",
        timestamp="2026-10-31 03:33:07",
        source="SystemKernel",
        event_type="Process",
        message="System wake-up event triggered.",
        parsed_time=datetime(2026, 10, 31, 3, 33, 7),
    )
    scored = detector.evaluate_event(event)
    assert scored.mystery_score >= 35
    assert any("Witching Hour" in r for r in scored.reasons)
    assert scored.is_anomaly
    assert scored.classification == "Fictional Anomaly"


def test_paranormal_keywords_and_patterns(detector: MysteryDetector):
    """Verify paranormal keywords and corrupted addresses drive up score into High/Paranormal."""
    event = LogEvent(
        id="para_1",
        timestamp="2026-10-31 03:33:07",
        source="ProcessWatcher",
        event_type="Process",
        message="Spontaneous execution of daemon.spirit at hex address 0xDEADBEEF.",
        parsed_time=datetime(2026, 10, 31, 3, 33, 7),
    )
    scored = detector.evaluate_event(event)
    # Witching hour (35) + keywords/patterns should trigger Paranormal severity
    assert scored.mystery_score >= 80
    assert scored.severity == "Paranormal"
    assert scored.is_anomaly
    assert any("daemon.spirit" in r or "pointer" in r for r in scored.reasons)


def test_phantom_device_detection(detector: MysteryDetector):
    """Verify fictional phantom USB device connection is flagged."""
    event = LogEvent(
        id="dev_1",
        timestamp="2026-10-31 02:10:00",
        source="USBHub",
        event_type="Device",
        message="Unregistered phantom peripheral connected [VID:0x0000 PID:0xDEAD].",
        parsed_time=datetime(2026, 10, 31, 2, 10, 0),
    )
    scored = detector.evaluate_event(event)
    assert scored.is_anomaly
    assert any("phantom" in r.lower() for r in scored.reasons)


def test_repeated_failed_login_burst(detector: MysteryDetector):
    """Verify that multiple failed logins trigger a burst pattern boost."""
    events = [
        LogEvent(
            id=f"auth_{i}",
            timestamp=f"2026-10-31 03:15:0{i}",
            source="AuthDaemon",
            event_type="Authentication",
            message=f"Simulated login failed for user guest_from_beyond (attempt {i})",
            details={"user": "guest_from_beyond"},
            parsed_time=datetime(2026, 10, 31, 3, 15, i),
        )
        for i in range(1, 4)
    ]
    scored_events, summary = detector.analyze_events(events)
    assert summary.anomalies_detected == 3
    assert any("Repeated failed authentication burst detected." in s.reasons for s in scored_events)
    assert summary.threat_level in ["Spooky 🟠", "Paranormal Surge 🟣"]


def test_empty_events_list(detector: MysteryDetector):
    """Verify empty event list produces an empty summary without errors."""
    scored_events, summary = detector.analyze_events([])
    assert scored_events == []
    assert summary.total_events == 0
    assert summary.anomalies_detected == 0
    assert summary.threat_level == "Calm 🟢"
