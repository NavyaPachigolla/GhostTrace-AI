"""GhostTrace AI - Built-in Sample Investigation Cases.

Provides pre-packaged paranormal test cases that users can inspect and
analyze immediately with zero file setup.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from ghosttrace.log_reader import LogEvent, LogReader


@dataclass
class SampleCase:
    """Metadata and definition of a built-in fictional investigation case."""
    case_id: str
    title: str
    subtitle: str
    description: str
    expected_findings: List[str]
    filename: str
    difficulty: str  # "Introductory", "Intermediate", "Advanced"
    tags: List[str]

    def get_file_path(self, base_dir: Optional[Path] = None) -> Path:
        """Resolve the file path to this case's log file."""
        if base_dir is None:
            # Default to sample_data relative to repo root
            base_dir = Path(__file__).resolve().parent.parent / "sample_data"
        return base_dir / self.filename


SAMPLE_CASES: Dict[str, SampleCase] = {
    "midnight_process": SampleCase(
        case_id="midnight_process",
        title="Case 001: The Midnight Process",
        subtitle="Spontaneous daemon execution during the witching hour",
        description=(
            "At 03:33 AM on Halloween night, the operating system kernel registered "
            "the sudden execution of 'daemon.spirit' without any parent PID. "
            "Memory allocations spiked at address 0xDEADBEEF, and an audio whisper thread "
            "listened on a dormant microphone before the process evaporated."
        ),
        expected_findings=[
            "Witching hour execution at exactly 03:33:07 AM",
            "Unregistered process 'daemon.spirit' spawned without parent PID",
            "Corrupt hex memory pointer '0xDEADBEEF' (333 MB)",
            "Dormant virtual microphone whisper thread #0333",
            "Abrupt termination with exit code 0x0000NULL",
        ],
        filename="midnight_process.json",
        difficulty="Introductory",
        tags=["Process", "Witching Hour", "Memory", "Ghost Daemon"],
    ),
    "forgotten_server": SampleCase(
        case_id="forgotten_server",
        title="Case 002: The Forgotten Server",
        subtitle="Telemetry heartbeats from decommissioned node 13",
        description=(
            "Server Rack 13 was decommissioned three years ago and unplugged from the main network. "
            "Yet at midnight, the telemetry bus received heartbeats from its IP, followed by "
            "simulated SSH login attempts from an identity called 'guest_from_beyond' and "
            "a sharp thermal plunge to 2.1°C."
        ),
        expected_findings=[
            "Heartbeat received from decommissioned server node 13",
            "Simulated brute-force authentication burst from 'guest_from_beyond'",
            "Unregistered virtual terminal 'tty_phantom'",
            "Localized freezing thermal drop to 2.1°C in Bay 13",
        ],
        filename="forgotten_server.json",
        difficulty="Intermediate",
        tags=["Server Room", "Authentication", "Thermal Drop", "Phantom Node"],
    ),
    "returning_file": SampleCase(
        case_id="returning_file",
        title="Case 003: The File That Returned",
        subtitle="A deleted archive that resurrects and rewrites its own history",
        description=(
            "An archivist permanently erased 'whispers_1999.bak' before leaving for the night. "
            "At 03:00 AM, the file reappeared in the Windows Temp directory with zero bytes, "
            "rewrote its own creation timestamp backwards by 27 years, and locked itself against "
            "the antivirus scanner with an unknown entity handle."
        ),
        expected_findings=[
            "Permanent deletion preceded midnight by 10 minutes",
            "Spontaneous resurrection in C:\\Windows\\Temp at 03:00:15 AM",
            "Temporal manipulation: timestamp rewritten backwards to October 1999",
            "File handle locked by phantom entity error code ACCESS_LOCKED_GHOST",
            "Vanished again during early morning cache sweep",
        ],
        filename="returning_file.json",
        difficulty="Advanced",
        tags=["FileSystem", "Time Distortion", "Resurrected File", "Retro"],
    ),
    "phantom_peripheral": SampleCase(
        case_id="phantom_peripheral",
        title="Case 004: The Phantom Peripheral",
        subtitle="An unregistered USB device injecting spectral keystrokes",
        description=(
            "A fictional USB HID device with vendor ID 0x0000 and product ID 0xDEAD "
            "hotplugged into the root hub at 03:14 AM. In five seconds, it typed a cryptic "
            "message into the terminal before disappearing without an unmount handshake."
        ),
        expected_findings=[
            "Unregistered peripheral with null vendor ID (0x0000) and product 0xDEAD",
            "High-speed simulated keystroke injection at 120 WPM",
            "Cryptic message: 'WHY DID YOU TURN OFF THE SCREEN'",
            "Phantom disconnect without bus handshake",
        ],
        filename="phantom_peripheral.json",
        difficulty="Introductory",
        tags=["Device", "USB Hotplug", "Keystrokes", "Haunted Hardware"],
    ),
    "haunted_syslog": SampleCase(
        case_id="haunted_syslog",
        title="Case 005: Haunted Syslog (Plain Text)",
        subtitle="Standard text log demonstration with multiple anomaly categories",
        description=(
            "Demonstrates plain-text syslog file parsing. Contains midnight cron jobs, "
            "a 03:33 AM daemon execution, repeated simulated password failures, and an echo file."
        ),
        expected_findings=[
            "Successful parsing of standard plain-text timestamp format",
            "Detection of daemon.spirit and 0xDEADBEEF hex address",
            "Repeated authentication failure burst for root_null",
            "Cryptic echo_0333.wav file creation",
        ],
        filename="haunted_syslog.log",
        difficulty="Intermediate",
        tags=["Plain Text", "Syslog", "Multi-Anomaly"],
    ),
}


class SampleCaseManager:
    """Manages loading and querying built-in investigation cases."""

    def __init__(self, sample_dir: Optional[Path] = None):
        if sample_dir is None:
            self.sample_dir = Path(__file__).resolve().parent.parent / "sample_data"
        else:
            self.sample_dir = sample_dir
        self.reader = LogReader(allowed_base_dir=self.sample_dir.parent)

    def list_cases(self) -> List[SampleCase]:
        """Return all available sample cases."""
        return list(SAMPLE_CASES.values())

    def get_case(self, case_id: str) -> Optional[SampleCase]:
        """Get case metadata by case_id."""
        return SAMPLE_CASES.get(case_id)

    def load_case_events(self, case_id: str) -> List[LogEvent]:
        """Load and parse the events for a given sample case."""
        case = self.get_case(case_id)
        if case is None:
            raise ValueError(f"Unknown sample case ID: '{case_id}'")

        file_path = case.get_file_path(self.sample_dir)
        if not file_path.exists():
            raise FileNotFoundError(f"Sample data file not found: {file_path}")

        return self.reader.read_file(file_path)
