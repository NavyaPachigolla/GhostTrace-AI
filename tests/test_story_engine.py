"""Tests for GhostStoryEngine, Ollama integration, graceful fallbacks, and narrative styles."""

from unittest.mock import MagicMock, patch
import pytest

from ghosttrace.config import STORY_STYLES
from ghosttrace.log_reader import LogEvent
from ghosttrace.mystery_detector import MysteryDetector, ScoredEvent
from ghosttrace.story_engine import GhostStoryEngine


@pytest.fixture
def sample_scored_events():
    detector = MysteryDetector()
    events = [
        LogEvent(
            id="e1",
            timestamp="2026-10-31 03:33:07",
            source="SystemKernel",
            event_type="Process",
            message="Spontaneous execution of daemon.spirit at address 0xDEADBEEF.",
        ),
        LogEvent(
            id="e2",
            timestamp="2026-10-31 03:34:00",
            source="ProcessWatcher",
            event_type="Process",
            message="Daemon terminated with exit code 0x0000NULL.",
        ),
    ]
    scored, _ = detector.analyze_events(events)
    return scored


def test_build_prompt_incorporates_events(sample_scored_events):
    """Verify prompt builder embeds timestamps, process names, and reasons."""
    engine = GhostStoryEngine()
    sys_prompt, user_prompt = engine.build_prompt(
        sample_scored_events,
        case_name="Case 001: The Midnight Process",
        style_key="haunted_computer",
    )
    assert "paranormal" in sys_prompt.lower()
    assert "03:33:07" in user_prompt
    assert "daemon.spirit" in user_prompt
    assert "0xDEADBEEF" in user_prompt


def test_fallback_story_generation(sample_scored_events):
    """Verify procedural fallback produces a coherent story mentioning the log evidence."""
    engine = GhostStoryEngine(ollama_url="http://invalid-nonexistent-host:9999")
    result = engine.generate_story(
        sample_scored_events,
        case_name="Test Case",
        style_key="haunted_computer",
        force_fallback=True,
    )
    assert result.is_fallback
    assert "Fallback" in result.engine
    assert "03:33:07" in result.text
    assert "daemon.spirit" in result.text
    assert len(result.text) > 200


def test_all_styles_fallback(sample_scored_events):
    """Verify all 4 required story styles generate distinct fallback texts."""
    engine = GhostStoryEngine()
    generated_texts = set()

    for style_key in STORY_STYLES.keys():
        result = engine.generate_story(
            sample_scored_events,
            case_name="Style Variety Test",
            style_key=style_key,
            force_fallback=True,
        )
        assert result.style_key == style_key
        assert result.text not in generated_texts
        generated_texts.add(result.text)

    assert len(generated_texts) == 4


def test_missing_ollama_graceful_fallback(sample_scored_events):
    """Verify that an unavailable Ollama service automatically falls back without raising an exception."""
    # Point to an invalid port that will immediately refuse connection
    engine = GhostStoryEngine(ollama_url="http://127.0.0.1:59999")
    is_connected, _, status = engine.check_connection()
    assert not is_connected
    assert "not running" in status or "error" in status.lower()

    # Story generation should automatically fall back
    result = engine.generate_story(
        sample_scored_events,
        case_name="Offline Test",
        style_key="digital_ghost",
    )
    assert result.is_fallback
    assert "Fallback" in result.engine


def test_mocked_ollama_successful_generation(sample_scored_events):
    """Verify that when Ollama returns HTTP 200, its response is cleanly formatted."""
    engine = GhostStoryEngine(ollama_url="http://localhost:11434", model_name="qwen2.5:3b")

    mock_tags_resp = MagicMock()
    mock_tags_resp.status_code = 200
    mock_tags_resp.json.return_value = {"models": [{"name": "qwen2.5:3b"}]}

    mock_gen_resp = MagicMock()
    mock_gen_resp.status_code = 200
    mock_gen_resp.json.return_value = {
        "response": "The screen flickered violently as the clock struck 03:33:07. A ghost inhabited the kernel."
    }

    with patch("requests.get", return_value=mock_tags_resp), patch("requests.post", return_value=mock_gen_resp):
        result = engine.generate_story(
            sample_scored_events,
            case_name="Mocked Case",
            style_key="abandoned_server",
        )
        assert not result.is_fallback
        assert "Ollama" in result.engine
        assert "clock struck 03:33:07" in result.text
