"""GhostTrace AI - Paranormal Investigation Timeline.

Provides filtering, sorting, and structured timeline representation
for paranormal log event investigations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

from ghosttrace.mystery_detector import ScoredEvent


@dataclass
class TimelineFilter:
    """Filter parameters for timeline queries."""
    severities: Optional[Set[str]] = None  # {"Low", "Medium", "High", "Paranormal"}
    event_types: Optional[Set[str]] = None
    anomalies_only: bool = False
    search_keyword: str = ""
    start_hour: Optional[int] = None
    end_hour: Optional[int] = None


class InvestigationTimeline:
    """Manages an interactive chronological sequence of scored events."""

    def __init__(self, scored_events: List[ScoredEvent]):
        self.scored_events = scored_events

    def get_available_event_types(self) -> List[str]:
        """Return unique event types present in the investigation."""
        return sorted(list({e.event.event_type for e in self.scored_events if e.event.event_type}))

    def get_available_severities(self) -> List[str]:
        """Return unique severity levels present in the investigation."""
        order = ["Paranormal", "High", "Medium", "Low"]
        present = {e.severity for e in self.scored_events}
        return [s for s in order if s in present]

    def filter_events(self, criteria: TimelineFilter) -> List[ScoredEvent]:
        """Filter events based on user-specified criteria."""
        filtered = self.scored_events

        # Filter by anomaly status
        if criteria.anomalies_only:
            filtered = [e for e in filtered if e.is_anomaly]

        # Filter by severity
        if criteria.severities:
            filtered = [e for e in filtered if e.severity in criteria.severities]

        # Filter by event type
        if criteria.event_types:
            filtered = [e for e in filtered if e.event.event_type in criteria.event_types]

        # Filter by search keyword
        if criteria.search_keyword:
            kw = criteria.search_keyword.lower().strip()
            filtered = [
                e for e in filtered
                if kw in e.event.message.lower()
                or kw in e.event.source.lower()
                or kw in e.event.event_type.lower()
                or any(kw in r.lower() for r in e.reasons)
            ]

        # Filter by hour range
        if criteria.start_hour is not None and criteria.end_hour is not None:
            time_filtered = []
            for e in filtered:
                if e.event.parsed_time is not None:
                    h = e.event.parsed_time.hour
                    if criteria.start_hour <= h <= criteria.end_hour:
                        time_filtered.append(e)
                else:
                    # If time couldn't be parsed, keep it so it's not hidden
                    time_filtered.append(e)
            filtered = time_filtered

        return filtered

    def get_timeline_stats(self) -> Dict:
        """Calculate statistics for the timeline view."""
        total = len(self.scored_events)
        if total == 0:
            return {
                "total": 0,
                "anomalies": 0,
                "peak_score": 0,
                "paranormal_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
            }

        anomalies = [e for e in self.scored_events if e.is_anomaly]
        paranormal = [e for e in self.scored_events if e.severity == "Paranormal"]
        high = [e for e in self.scored_events if e.severity == "High"]
        medium = [e for e in self.scored_events if e.severity == "Medium"]
        low = [e for e in self.scored_events if e.severity == "Low"]

        return {
            "total": total,
            "anomalies": len(anomalies),
            "peak_score": max((e.mystery_score for e in self.scored_events), default=0),
            "paranormal_count": len(paranormal),
            "high_count": len(high),
            "medium_count": len(medium),
            "low_count": len(low),
        }
