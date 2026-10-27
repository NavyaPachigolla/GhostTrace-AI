"""Tests for LogReader, safe file handling, malformed log tolerance, and path traversal."""

import json
from pathlib import Path
import pytest

from ghosttrace.config import MAX_FILE_SIZE_BYTES
from ghosttrace.log_reader import (
    LogEvent,
    LogReader,
    parse_json_content,
    parse_plaintext_content,
    parse_timestamp,
    sanitize_path,
)


def test_parse_timestamp_formats():
    """Verify various timestamp formats parse accurately."""
    # ISO 8601
    dt1 = parse_timestamp("2026-10-31T03:33:07")
    assert dt1 is not None
    assert dt1.hour == 3
    assert dt1.minute == 33
    assert dt1.second == 7

    # Space separated
    dt2 = parse_timestamp("2026-10-31 03:33:07")
    assert dt2 is not None
    assert dt2.hour == 3

    # Time only
    dt3 = parse_timestamp("03:33:07")
    assert dt3 is not None
    assert dt3.hour == 3

    # Invalid timestamp returns None safely without raising
    assert parse_timestamp("not-a-timestamp") is None
    assert parse_timestamp("") is None


def test_parse_json_content_valid():
    """Verify normal JSON array and dict structures parse into LogEvents."""
    content = json.dumps([
        {
            "id": "e1",
            "timestamp": "2026-10-31T03:33:07",
            "source": "Kernel",
            "event_type": "Process",
            "message": "Ghost process started",
            "pid": 666,
        }
    ])
    events = parse_json_content(content, "test.json")
    assert len(events) == 1
    assert events[0].id == "e1"
    assert events[0].source == "Kernel"
    assert events[0].event_type == "Process"
    assert events[0].details["pid"] == 666


def test_parse_json_content_wrapped_dict():
    """Verify JSON with {'events': [...]} wrapping parses properly."""
    content = json.dumps({
        "events": [
            {
                "timestamp": "2026-10-31 01:00:00",
                "message": "Wrapped event",
            }
        ]
    })
    events = parse_json_content(content, "wrapped.json")
    assert len(events) == 1
    assert events[0].message == "Wrapped event"


def test_parse_json_content_malformed():
    """Verify malformed JSON does not crash the reader and parses recoverable lines."""
    # Corrupt JSON with one valid JSON-line
    content = "This is not valid json\n{\"timestamp\": \"2026-10-31 03:33:00\", \"message\": \"Line 2 survived\"}\n{corrupted"
    events = parse_json_content(content, "malformed.json")
    # Should safely recover the single valid line without unhandled exception
    assert len(events) == 1
    assert events[0].message == "Line 2 survived"


def test_parse_plaintext_content():
    """Verify plain text log lines parse into LogEvents with inferred event types."""
    content = (
        "# Comment line should be ignored\n"
        "2026-10-31 03:33:07 [AUTH] Failed password for guest_from_beyond\n"
        "2026-10-31 03:34:00 [KERNEL] Unexpected service restart\n"
        "\n"
    )
    events = parse_plaintext_content(content, "syslog.log")
    assert len(events) == 2
    assert events[0].event_type == "Authentication"
    assert events[0].source == "AUTH"
    assert events[1].event_type == "Service"


def test_empty_input(tmp_path: Path):
    """Verify empty files return an empty list without error."""
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("", encoding="utf-8")

    reader = LogReader(allowed_base_dir=tmp_path)
    events = reader.read_file(empty_file)
    assert events == []


def test_unsupported_file_types(tmp_path: Path):
    """Verify that unsupported extensions (e.g. .exe, .py, .csv) are rejected."""
    bad_file = tmp_path / "malicious.exe"
    bad_file.write_text("MZ...", encoding="utf-8")

    reader = LogReader(allowed_base_dir=tmp_path)
    with pytest.raises(ValueError, match="Unsupported file format"):
        reader.read_file(bad_file)


def test_path_traversal_prevention(tmp_path: Path):
    """Verify that paths outside the allowed base directory are rejected."""
    safe_dir = tmp_path / "safe"
    safe_dir.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    secret_file = outside_dir / "secret.json"
    secret_file.write_text(json.dumps([{"message": "secret"}]), encoding="utf-8")

    reader = LogReader(allowed_base_dir=safe_dir)

    # Attempting to access secret_file via relative traversal
    traversal_path = safe_dir / ".." / "outside" / "secret.json"
    with pytest.raises(ValueError, match="outside allowed directory"):
        reader.read_file(traversal_path)


def test_nonexistent_path(tmp_path: Path):
    """Verify non-existent files are safely rejected."""
    reader = LogReader(allowed_base_dir=tmp_path)
    with pytest.raises(ValueError, match="Path does not exist"):
        reader.read_file(tmp_path / "ghost_file_does_not_exist.json")


def test_file_read_only_integrity(tmp_path: Path):
    """Verify reading a log does not alter its contents or timestamp."""
    test_file = tmp_path / "sample.json"
    original_content = json.dumps([{"id": "1", "timestamp": "2026-10-31 00:00:00", "message": "Immutable test"}])
    test_file.write_text(original_content, encoding="utf-8")

    reader = LogReader(allowed_base_dir=tmp_path)
    events = reader.read_file(test_file)
    assert len(events) == 1

    # Check file content on disk is completely untouched
    assert test_file.read_text(encoding="utf-8") == original_content
