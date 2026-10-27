"""GhostTrace AI - Safe Activity Log Scanner.

Reads user-selected sample log files (JSON, LOG, TXT) with strict path validation,
read-only guarantees, malformed log tolerance, and zero system alteration.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
import uuid

from ghosttrace.config import MAX_FILE_SIZE_BYTES, SUPPORTED_EXTENSIONS


@dataclass
class LogEvent:
    """Represents a normalized log event read from a sample file."""
    id: str
    timestamp: str
    source: str
    event_type: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    raw_entry: str = ""
    file_source: str = ""
    parsed_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "source": self.source,
            "event_type": self.event_type,
            "message": self.message,
            "details": self.details,
            "raw_entry": self.raw_entry,
            "file_source": self.file_source,
        }


# Regex patterns for parsing timestamps from plain-text log lines
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2026-10-31T03:33:07 or 2026-10-31 03:33:07
    re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)"),
    # Syslog: Oct 31 03:33:07
    re.compile(r"([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"),
    # Simple time: 03:33:07
    re.compile(r"(\b\d{2}:\d{2}:\d{2}\b)"),
]


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """Safely attempt to parse various timestamp formats."""
    if not ts_str:
        return None

    clean = ts_str.strip()
    # Try ISO
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y/%m/%d %H:%M:%S",
        "%H:%M:%S",
    ):
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            pass

    # Try Syslog with current year
    try:
        current_year = datetime.now().year
        return datetime.strptime(f"{current_year} {clean}", "%Y %b %d %H:%M:%S")
    except ValueError:
        pass

    return None


def sanitize_path(target_path: Path, allowed_base: Optional[Path] = None) -> Tuple[bool, str, Optional[Path]]:
    """Validate that target_path is safe, exists, and does not escape allowed_base.

    Returns:
        (is_valid, error_message, resolved_path)
    """
    try:
        resolved = target_path.resolve()
    except (RuntimeError, ValueError) as e:
        return False, f"Invalid path resolution: {e}", None

    if not resolved.exists():
        return False, f"Path does not exist: {target_path}", None

    if allowed_base is not None:
        try:
            resolved_base = allowed_base.resolve()
            # Check if resolved is within resolved_base
            resolved.relative_to(resolved_base)
        except ValueError:
            return False, f"Path traversal rejected: {target_path} is outside allowed directory", None

    return True, "", resolved


def parse_json_content(content: str, filename: str) -> List[LogEvent]:
    """Parse JSON log content from string into LogEvent objects."""
    events: List[LogEvent] = []
    if not content or not content.strip():
        return events

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Try JSON Lines (one JSON object per line)
        for line_num, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                line_data = json.loads(line)
                if isinstance(line_data, dict):
                    event = _create_event_from_dict(line_data, filename, line)
                    events.append(event)
            except json.JSONDecodeError:
                continue
        return events

    raw_list: List[Dict[str, Any]] = []
    if isinstance(data, list):
        raw_list = [item for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        if "events" in data and isinstance(data["events"], list):
            raw_list = [item for item in data["events"] if isinstance(item, dict)]
        elif "logs" in data and isinstance(data["logs"], list):
            raw_list = [item for item in data["logs"] if isinstance(item, dict)]
        else:
            raw_list = [data]

    for item in raw_list:
        event = _create_event_from_dict(item, filename, json.dumps(item))
        events.append(event)

    return events


def _create_event_from_dict(item: Dict[str, Any], filename: str, raw_str: str) -> LogEvent:
    """Normalize a raw dictionary into a LogEvent."""
    ts = str(item.get("timestamp") or item.get("time") or item.get("date") or "Unknown Time")
    source = str(item.get("source") or item.get("service") or item.get("host") or "System")
    event_type = str(item.get("event_type") or item.get("type") or item.get("category") or "General")
    message = str(item.get("message") or item.get("description") or item.get("event") or "No message")
    event_id = str(item.get("id") or uuid.uuid4().hex[:8])

    # Remaining fields become details
    reserved = {"id", "timestamp", "time", "date", "source", "service", "host", "event_type", "type", "category", "message", "description", "event"}
    details = {k: v for k, v in item.items() if k not in reserved}

    parsed = parse_timestamp(ts)

    return LogEvent(
        id=event_id,
        timestamp=ts,
        source=source,
        event_type=event_type,
        message=message,
        details=details,
        raw_entry=raw_str,
        file_source=filename,
        parsed_time=parsed,
    )


def parse_plaintext_content(content: str, filename: str) -> List[LogEvent]:
    """Parse plain text log content into normalized LogEvents."""
    events: List[LogEvent] = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, start=1):
        line_clean = line.strip()
        if not line_clean or line_clean.startswith("#"):
            continue

        ts_str = "Unknown Time"
        matched_ts = None
        for pat in TIMESTAMP_PATTERNS:
            match = pat.search(line_clean)
            if match:
                ts_str = match.group(1)
                matched_ts = parse_timestamp(ts_str)
                break

        # Extract event type and source heuristic
        # e.g. "2026-10-31 03:33:07 [AUTH] Failed password for root"
        bracket_match = re.search(r"\[([A-Za-z0-9_\-]+)\]", line_clean)
        source = bracket_match.group(1) if bracket_match else "KernelLog"

        event_type = "System"
        lower_line = line_clean.lower()
        if any(w in lower_line for w in ["login", "auth", "password", "session", "user"]):
            event_type = "Authentication"
        elif any(w in lower_line for w in ["process", "pid", "exec", "started", "terminated", "spawn"]):
            event_type = "Process"
        elif any(w in lower_line for w in ["usb", "device", "hardware", "peripheral", "pci"]):
            event_type = "Device"
        elif any(w in lower_line for w in ["file", "directory", "resurrect", "delete", "write"]):
            event_type = "FileSystem"
        elif any(w in lower_line for w in ["service", "daemon", "restart", "systemd"]):
            event_type = "Service"

        events.append(
            LogEvent(
                id=f"txt_{idx:04d}",
                timestamp=ts_str,
                source=source,
                event_type=event_type,
                message=line_clean,
                details={"line_number": idx},
                raw_entry=line_clean,
                file_source=filename,
                parsed_time=matched_ts,
            )
        )

    return events


class LogReader:
    """Safe, read-only scanner for user-selected log files and directories."""

    def __init__(self, allowed_base_dir: Optional[Path] = None):
        self.allowed_base_dir = allowed_base_dir

    def read_file(self, file_path: Path) -> List[LogEvent]:
        """Safely read a single log file without modifying it."""
        is_valid, err, resolved = sanitize_path(file_path, self.allowed_base_dir)
        if not is_valid or resolved is None:
            raise ValueError(f"File access rejected: {err}")

        if not resolved.is_file():
            raise ValueError(f"Path is not a regular file: {resolved}")

        suffix = resolved.suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format '{suffix}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        # Check file size limit
        file_size = resolved.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size exceeds safety limit ({file_size} > {MAX_FILE_SIZE_BYTES} bytes)"
            )

        if file_size == 0:
            return []

        # Read safely in read-only mode with UTF-8 and fallback
        try:
            content = resolved.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            raise IOError(f"Failed to read file '{resolved.name}': {e}") from e

        if suffix == ".json":
            return parse_json_content(content, resolved.name)
        else:
            return parse_plaintext_content(content, resolved.name)

    def scan_directory(self, dir_path: Path) -> List[LogEvent]:
        """Safely scan all supported log files within a directory."""
        is_valid, err, resolved_dir = sanitize_path(dir_path, self.allowed_base_dir)
        if not is_valid or resolved_dir is None:
            raise ValueError(f"Directory access rejected: {err}")

        if not resolved_dir.is_dir():
            raise ValueError(f"Path is not a directory: {resolved_dir}")

        all_events: List[LogEvent] = []

        # List files non-recursively for safety, ignoring hidden files
        for item in sorted(resolved_dir.iterdir()):
            if item.is_file() and not item.name.startswith("."):
                if item.suffix.lower() in SUPPORTED_EXTENSIONS:
                    try:
                        file_events = self.read_file(item)
                        all_events.extend(file_events)
                    except Exception:
                        # Continue scanning other valid files if one file fails
                        continue

        # Sort events chronologically if timestamps are parseable
        all_events.sort(key=lambda e: (e.parsed_time is None, e.parsed_time or datetime.min, e.timestamp))
        return all_events
