"""
Utility helpers for validation, parsing, aggregation.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple
from datetime import datetime, timezone
from collections import defaultdict, Counter
import math

from config import REQUIRED_FIELDS


def parse_timestamp(ts: str) -> Optional[datetime]:
    try:
        # Expecting ISO8601 with Z
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def is_error_status(code: int) -> bool:
    return 400 <= code <= 599


def safe_int(v: Any) -> Optional[int]:
    try:
        iv = int(v)
        return iv if iv >= 0 else None
    except Exception:
        return None


def safe_str(v: Any) -> Optional[str]:
    try:
        s = str(v)
        return s if s else None
    except Exception:
        return None


def validate_log_entry(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Ensure all required fields exist
    for f in REQUIRED_FIELDS:
        if f not in entry:
            return None

    ts = parse_timestamp(entry["timestamp"])
    endpoint = safe_str(entry["endpoint"])
    method = safe_str(entry["method"])
    rt = safe_int(entry["response_time_ms"])
    status = safe_int(entry["status_code"])
    user = safe_str(entry["user_id"])
    req_bytes = safe_int(entry["request_size_bytes"])
    resp_bytes = safe_int(entry["response_size_bytes"])

    if None in (ts, endpoint, method, rt, status, user, req_bytes, resp_bytes):
        return None

    return {
        "timestamp": ts,
        "endpoint": endpoint,
        "method": method.upper(),
        "response_time_ms": rt,
        "status_code": status,
        "user_id": user,
        "request_size_bytes": req_bytes,
        "response_size_bytes": resp_bytes,
    }


def aggregate_by_endpoint(valid_logs: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    stats: Dict[str, Dict[str, Any]] = {}
    for log in valid_logs:
        ep = log["endpoint"]
        s = stats.setdefault(
            ep,
            {
                "count": 0,
                "sum_rt": 0,
                "slowest": -math.inf,
                "fastest": math.inf,
                "error_count": 0,
                "status_counter": Counter(),
            },
        )
        s["count"] += 1
        s["sum_rt"] += log["response_time_ms"]
        s["slowest"] = max(s["slowest"], log["response_time_ms"])
        s["fastest"] = min(s["fastest"], log["response_time_ms"])
        if is_error_status(log["status_code"]):
            s["error_count"] += 1
        s["status_counter"][log["status_code"]] += 1
    return stats


def severity_for_response_time(avg_ms: float, thresholds: Dict[str, int]) -> Optional[str]:
    if avg_ms > thresholds["critical"]:
        return "critical"
    if avg_ms > thresholds["high"]:
        return "high"
    if avg_ms > thresholds["medium"]:
        return "medium"
    return None


def severity_for_error_rate(err_rate_percent: float, thresholds: Dict[str, float]) -> Optional[str]:
    if err_rate_percent > thresholds["critical"]:
        return "critical"
    if err_rate_percent > thresholds["high"]:
        return "high"
    if err_rate_percent > thresholds["medium"]:
        return "medium"
    return None


def hourly_bucket(dt: datetime) -> str:
    # Return "HH:00" in UTC
    return f"{dt.hour:02d}:00"


def sliding_window_counts(
    timestamps: List[datetime], window_minutes: int
) -> List[Tuple[datetime, int]]:
    # timestamps must be sorted
    counts: List[Tuple[datetime, int]] = []
    left = 0
    for right in range(len(timestamps)):
        start_time = timestamps[right]
        window_start = start_time - timedelta_minutes(window_minutes)
        while timestamps[left] < window_start:
            left += 1
        counts.append((start_time, right - left + 1))
    return counts


def timedelta_minutes(m: int):
    from datetime import timedelta

    return timedelta(minutes=m)
