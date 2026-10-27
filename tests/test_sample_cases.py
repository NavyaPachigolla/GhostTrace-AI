"""Tests for built-in sample cases, case loading integrity, and timeline management."""

from pathlib import Path
import pytest

from ghosttrace.mystery_detector import MysteryDetector
from ghosttrace.sample_cases import SAMPLE_CASES, SampleCaseManager
from ghosttrace.timeline import InvestigationTimeline, TimelineFilter


@pytest.fixture
def case_manager():
    return SampleCaseManager()


@pytest.fixture
def detector():
    return MysteryDetector()


def test_all_sample_cases_exist_and_load(case_manager: SampleCaseManager):
    """Verify all defined sample cases exist on disk and load valid events."""
    cases = case_manager.list_cases()
    assert len(cases) >= 3

    for case in cases:
        events = case_manager.load_case_events(case.case_id)
        assert len(events) > 0, f"Case {case.case_id} produced no events"
        # Check that events have non-empty messages and valid IDs
        for ev in events:
            assert ev.message
            assert ev.id
            assert ev.event_type


def test_sample_cases_produce_fictional_anomalies(
    case_manager: SampleCaseManager, detector: MysteryDetector
):
    """Verify that every sample case contains at least one flagged fictional anomaly."""
    for case in case_manager.list_cases():
        events = case_manager.load_case_events(case.case_id)
        scored, summary = detector.analyze_events(events)

        assert summary.anomalies_detected >= 1, f"Case {case.case_id} had 0 anomalies"
        assert summary.peak_mystery_score >= 35
        assert summary.threat_level != "Calm 🟢"


def test_timeline_filtering(case_manager: SampleCaseManager, detector: MysteryDetector):
    """Verify investigation timeline filters events accurately."""
    events = case_manager.load_case_events("midnight_process")
    scored, _ = detector.analyze_events(events)
    timeline = InvestigationTimeline(scored)

    # Filter by anomalies only
    anomaly_events = timeline.filter_events(TimelineFilter(anomalies_only=True))
    assert len(anomaly_events) > 0
    assert all(e.is_anomaly for e in anomaly_events)

    # Filter by severity
    paranormal_events = timeline.filter_events(TimelineFilter(severities={"Paranormal"}))
    assert all(e.severity == "Paranormal" for e in paranormal_events)

    # Filter by search keyword
    spirit_events = timeline.filter_events(TimelineFilter(search_keyword="spirit"))
    assert len(spirit_events) >= 1
    assert any("spirit" in e.event.message.lower() for e in spirit_events)

    # Check stats
    stats = timeline.get_timeline_stats()
    assert stats["total"] == len(events)
    assert stats["anomalies"] > 0
    assert stats["peak_score"] > 0


def test_unknown_case_id_raises_value_error(case_manager: SampleCaseManager):
    """Verify attempting to load an unregistered case ID raises ValueError."""
    with pytest.raises(ValueError, match="Unknown sample case ID"):
        case_manager.load_case_events("non_existent_case_999")
