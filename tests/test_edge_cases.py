# Python
import pytest
from datetime import datetime, timezone

from function import analyze_api_logs

def test_empty_input():
    result = analyze_api_logs([])
    assert result["summary"]["total_requests"] == 0
    assert result["summary"]["time_range"]["start"] is None
    assert result["endpoint_stats"] == []
    assert result["anomalies"] == []

def test_single_log_entry():
    log = {
        "timestamp": datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": 150,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 2048,
    }
    result = analyze_api_logs([log])
    assert result["summary"]["total_requests"] == 1
    assert len(result["endpoint_stats"]) == 1
    assert result["endpoint_stats"][0]["endpoint"] == "/api/users"

def test_malformed_missing_fields_skipped():
    bad = {
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": 150,
        # missing status_code
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 2048,
    }
    good = dict(bad)
    good["status_code"] = 200
    result = analyze_api_logs([bad, good])
    assert result["summary"]["total_requests"] == 1

def test_invalid_timestamp_skipped():
    bad = {
        "timestamp": "bad-ts",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": 150,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 2048,
    }
    result = analyze_api_logs([bad])
    assert result["summary"]["total_requests"] == 0

def test_negative_numbers_skipped():
    bad = {
        "timestamp": "2025-01-15T10:00:00Z",
        "endpoint": "/api/users",
        "method": "GET",
        "response_time_ms": -10,
        "status_code": 200,
        "user_id": "user_1",
        "request_size_bytes": 512,
        "response_size_bytes": 2048,
    }
    result = analyze_api_logs([bad])
    assert result["summary"]["total_requests"] == 0

def test_error_rate_severity_levels():
    logs = []
    for i in range(20):
        logs.append({
            "timestamp": f"2025-01-15T10:00:{i:02d}Z",
            "endpoint": "/api/payments",
            "method": "POST",
            "response_time_ms": 900,
            "status_code": 500 if i < 3 else 200,  # 15% errors
            "user_id": "u",
            "request_size_bytes": 100,
            "response_size_bytes": 1000,
        })
    result = analyze_api_logs(logs)
    issues = [i for i in result["performance_issues"] if i["type"] == "high_error_rate" and i["endpoint"] == "/api/payments"]
    assert issues, "Expected high_error_rate issue"
    assert issues[0]["severity"] in {"high", "critical", "medium"}
