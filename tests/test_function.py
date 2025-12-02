# Python
import json
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

import pytest

from function import analyze_api_logs

def make_log(
    ts: datetime,
    endpoint: str = "/api/users",
    method: str = "GET",
    rt_ms: int = 120,
    status: int = 200,
    user_id: str = "user_001",
    req_bytes: int = 512,
    resp_bytes: int = 2048,
) -> Dict[str, Any]:
    return {
        "timestamp": ts.isoformat().replace("+00:00", "Z"),
        "endpoint": endpoint,
        "method": method,
        "response_time_ms": rt_ms,
        "status_code": status,
        "user_id": user_id,
        "request_size_bytes": req_bytes,
        "response_size_bytes": resp_bytes,
    }

def test_core_summary_and_endpoint_stats_small():
    base = datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
    logs = [
        make_log(base + timedelta(seconds=i * 10), endpoint="/api/users", rt_ms=100, status=200, user_id="u1")
        for i in range(5)
    ] + [
        make_log(base + timedelta(seconds=60 + i * 10), endpoint="/api/payments", rt_ms=900, status=500, user_id="u2")
        for i in range(2)
    ]
    result = analyze_api_logs(logs)
    assert result["summary"]["total_requests"] == 7
    assert any(s["endpoint"] == "/api/users" for s in result["endpoint_stats"])
    assert any(s["endpoint"] == "/api/payments" for s in result["endpoint_stats"])
    assert "cost_analysis" in result
    assert "anomalies" in result

def test_hourly_distribution_and_top_users():
    base = datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
    logs = []
    for i in range(10):
        logs.append(make_log(base + timedelta(minutes=i), user_id=f"user_{i%3}"))
    result = analyze_api_logs(logs)
    assert "10:00" in result["hourly_distribution"]
    assert len(result["top_users_by_requests"]) <= 5

@pytest.mark.performance
def test_performance_10k_under_2_seconds():
    base = datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
    logs: List[Dict[str, Any]] = []
    endpoints = ["/api/users", "/api/search", "/api/payments", "/api/reports"]
    users = [f"user_{i}" for i in range(100)]
    # Create 12,000 logs spread over 60 minutes
    n = 12000
    for i in range(n):
        ts = base + timedelta(seconds=i % 3600)  # keep within 1 hour for distributions
        ep = endpoints[i % len(endpoints)]
        user = users[i % len(users)]
        status = 200 if i % 10 else 500  # 10% errors
        rt = 100 + (i % 300)  # vary response time up to 399ms
        resp_bytes = 500 + (i % 15000)  # vary size
        logs.append(
            make_log(ts, endpoint=ep, rt_ms=rt, status=status, user_id=user, resp_bytes=resp_bytes)
        )

    start = time.perf_counter()
    result = analyze_api_logs(logs)
    elapsed = time.perf_counter() - start

    assert result["summary"]["total_requests"] == n
    assert elapsed < 2.0, f"Processing {n} logs took {elapsed:.3f}s which exceeds 2s"
