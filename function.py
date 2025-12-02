"""
Main function: analyze_api_logs
Core analytics + Option A (Cost Estimation) + Option B (Anomaly Detection).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timezone

from config import (
    SEVERITY_THRESHOLDS_MS,
    ERROR_RATE_THRESHOLDS_PERCENT,
    COST_PER_REQUEST_USD,
    COST_PER_MS_EXECUTION_USD,
    MEMORY_COST_BRACKETS,
    REQUEST_SPIKE_WINDOW_MINUTES,
    REQUEST_SPIKE_MULTIPLIER,
    RESPONSE_DEGRADATION_MULTIPLIER,
    ERROR_CLUSTER_WINDOW_MINUTES,
    ERROR_CLUSTER_THRESHOLD,
    UNUSUAL_USER_SHARE_THRESHOLD,
    DEFAULT_SLOW_ENDPOINT_THRESHOLD_MS,
)
from utils import (
    validate_log_entry,
    aggregate_by_endpoint,
    severity_for_response_time,
    severity_for_error_rate,
    hourly_bucket,
    sliding_window_counts,
    timedelta_minutes,
)


def _most_common_status(counter: Counter) -> Optional[int]:
    if not counter:
        return None
    return counter.most_common(1)[0][0]


def _calc_summary(valid_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(valid_logs)
    if total == 0:
        return {
            "total_requests": 0,
            "time_range": {"start": None, "end": None},
            "avg_response_time_ms": 0,
            "error_rate_percentage": 0,
        }
    timestamps = [l["timestamp"] for l in valid_logs]
    start = min(timestamps).isoformat().replace("+00:00", "Z")
    end = max(timestamps).isoformat().replace("+00:00", "Z")
    sum_rt = sum(l["response_time_ms"] for l in valid_logs)
    avg_rt = sum_rt / total
    errors = sum(1 for l in valid_logs if 400 <= l["status_code"] <= 599)
    err_rate = (errors / total) * 100 if total else 0.0
    return {
        "total_requests": total,
        "time_range": {"start": start, "end": end},
        "avg_response_time_ms": round(avg_rt, 3),
        "error_rate_percentage": round(err_rate, 3),
    }


def _calc_endpoint_stats(valid_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_ep = aggregate_by_endpoint(valid_logs)
    stats: List[Dict[str, Any]] = []
    for ep, s in by_ep.items():
        avg_ms = (s["sum_rt"] / s["count"]) if s["count"] else 0
        stats.append(
            {
                "endpoint": ep,
                "request_count": s["count"],
                "avg_response_time_ms": round(avg_ms, 3),
                "slowest_request_ms": int(s["slowest"]) if s["slowest"] != float("-inf") else 0,
                "fastest_request_ms": int(s["fastest"]) if s["fastest"] != float("inf") else 0,
                "error_count": s["error_count"],
                "most_common_status": _most_common_status(s["status_counter"]),
            }
        )
    stats.sort(key=lambda x: x["endpoint"])
    return stats


def _detect_performance_issues(endpoint_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for s in endpoint_stats:
        sev = severity_for_response_time(s["avg_response_time_ms"], SEVERITY_THRESHOLDS_MS)
        if sev:
            issues.append(
                {
                    "type": "slow_endpoint",
                    "endpoint": s["endpoint"],
                    "avg_response_time_ms": s["avg_response_time_ms"],
                    "threshold_ms": DEFAULT_SLOW_ENDPOINT_THRESHOLD_MS,
                    "severity": sev,
                }
            )
        # Error rate severity per endpoint
        total = s["request_count"]
        err_rate = (s["error_count"] / total * 100) if total else 0.0
        err_sev = severity_for_error_rate(err_rate, ERROR_RATE_THRESHOLDS_PERCENT)
        if err_sev:
            issues.append(
                {
                    "type": "high_error_rate",
                    "endpoint": s["endpoint"],
                    "error_rate_percentage": round(err_rate, 3),
                    "severity": err_sev,
                }
            )
    return issues


def _recommendations(summary: Dict[str, Any], endpoint_stats: List[Dict[str, Any]]) -> List[str]:
    recs: List[str] = []
    # Caching recommendation for frequent GET endpoints will be finalized in Option D (ignored here),
    # but we can still suggest investigating slow endpoints and high error rate ones.
    for s in endpoint_stats:
        if s["avg_response_time_ms"] > SEVERITY_THRESHOLDS_MS["medium"]:
            recs.append(
                f"Investigate {s['endpoint']} performance (avg {s['avg_response_time_ms']}ms exceeds {SEVERITY_THRESHOLDS_MS['medium']}ms threshold)"
            )
        total = s["request_count"]
        err_rate = (s["error_count"] / total * 100) if total else 0.0
        if err_rate > ERROR_RATE_THRESHOLDS_PERCENT["medium"]:
            recs.append(f"Alert: {s['endpoint']} has {round(err_rate,3)}% error rate")
    return recs


def _hourly_distribution(valid_logs: List[Dict[str, Any]]) -> Dict[str, int]:
    dist: Dict[str, int] = defaultdict(int)
    for l in valid_logs:
        dist[hourly_bucket(l["timestamp"])] += 1
    return dict(sorted(dist.items()))


def _top_users(valid_logs: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    c = Counter(l["user_id"] for l in valid_logs)
    return [{"user_id": uid, "request_count": cnt} for uid, cnt in c.most_common(top_n)]


# Option A: Cost Estimation
def _memory_cost(bytes_count: int) -> float:
    for low, high, cost in MEMORY_COST_BRACKETS:
        if low <= bytes_count < high:
            return cost
    return 0.0


def _cost_analysis(valid_logs: List[Dict[str, Any]], endpoint_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_request_cost = len(valid_logs) * COST_PER_REQUEST_USD
    total_execution_cost = sum(l["response_time_ms"] * COST_PER_MS_EXECUTION_USD for l in valid_logs)
    total_memory_cost = sum(_memory_cost(l["response_size_bytes"]) for l in valid_logs)

    cost_by_ep_map: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "total_cost": 0.0})
    for l in valid_logs:
        ep = l["endpoint"]
        per_req = COST_PER_REQUEST_USD
        exec_cost = l["response_time_ms"] * COST_PER_MS_EXECUTION_USD
        mem_cost = _memory_cost(l["response_size_bytes"])
        total = per_req + exec_cost + mem_cost
        cost_by_ep_map[ep]["count"] += 1
        cost_by_ep_map[ep]["total_cost"] += total

    cost_by_endpoint: List[Dict[str, Any]] = []
    for ep, data in sorted(cost_by_ep_map.items()):
        per_request = data["total_cost"] / data["count"] if data["count"] else 0.0
        cost_by_endpoint.append(
            {
                "endpoint": ep,
                "total_cost": round(data["total_cost"], 6),
                "cost_per_request": round(per_request, 6),
            }
        )

    total_cost = total_request_cost + total_execution_cost + total_memory_cost

    # Simple optimization potential heuristic:
    # If endpoints with avg_response_time_ms > medium threshold were reduced to medium threshold,
    # potential savings equals reduction in execution cost proportional to time overage.
    potential_savings = 0.0
    for s in endpoint_stats:
        if s["avg_response_time_ms"] > SEVERITY_THRESHOLDS_MS["medium"]:
            over = s["avg_response_time_ms"] - SEVERITY_THRESHOLDS_MS["medium"]
            potential_savings += over * COST_PER_MS_EXECUTION_USD * s["request_count"]

    return {
        "total_cost_usd": round(total_cost, 6),
        "cost_breakdown": {
            "request_costs": round(total_request_cost, 6),
            "execution_costs": round(total_execution_cost, 6),
            "memory_costs": round(total_memory_cost, 6),
        },
        "cost_by_endpoint": cost_by_endpoint,
        "optimization_potential_usd": round(potential_savings, 6),
    }


# Option B: Anomaly Detection
def _anomalies(valid_logs: List[Dict[str, Any]], endpoint_stats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    anomalies: List[Dict[str, Any]] = []
    if not valid_logs:
        return anomalies

    # Request spikes per endpoint using 5-minute sliding window vs global average rate
    by_endpoint_ts: Dict[str, List[datetime]] = defaultdict(list)
    for l in valid_logs:
        by_endpoint_ts[l["endpoint"]].append(l["timestamp"])
    for ep, ts_list in by_endpoint_ts.items():
        ts_list.sort()
        # Normal average rate per 5 minutes = total_requests / (total_duration_minutes/5)
        duration_minutes = max(1, int((max(ts_list) - min(ts_list)).total_seconds() // 60) or 1)
        windows = max(1, duration_minutes / REQUEST_SPIKE_WINDOW_MINUTES)
        normal_rate = len(ts_list) / windows
        for t, count in sliding_window_counts(ts_list, REQUEST_SPIKE_WINDOW_MINUTES):
            if count > REQUEST_SPIKE_MULTIPLIER * normal_rate and count >= 1:
                anomalies.append(
                    {
                        "type": "request_spike",
                        "endpoint": ep,
                        "timestamp": t.isoformat().replace("+00:00", "Z"),
                        "normal_rate": int(normal_rate),
                        "actual_rate": int(count),
                        "severity": "high" if count > 2 * REQUEST_SPIKE_MULTIPLIER * normal_rate else "medium",
                    }
                )
                break  # report first spike

    # Response time degradation: compare recent average vs overall endpoint average
    # Use last 10% of logs for endpoint as "recent"
    by_endpoint_logs: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for l in valid_logs:
        by_endpoint_logs[l["endpoint"]].append(l)
    for ep, logs in by_endpoint_logs.items():
        logs.sort(key=lambda x: x["timestamp"])
        n = len(logs)
        if n < 5:
            continue
        recent = logs[max(0, int(n * 0.9)) :]
        recent_avg = sum(x["response_time_ms"] for x in recent) / len(recent)
        overall_avg = sum(x["response_time_ms"] for x in logs) / n
        if recent_avg > RESPONSE_DEGRADATION_MULTIPLIER * overall_avg and recent_avg > SEVERITY_THRESHOLDS_MS["medium"]:
            anomalies.append(
                {
                    "type": "response_time_degradation",
                    "endpoint": ep,
                    "recent_avg_ms": round(recent_avg, 3),
                    "overall_avg_ms": round(overall_avg, 3),
                    "severity": "high" if recent_avg > RESPONSE_DEGRADATION_MULTIPLIER * overall_avg * 1.5 else "medium",
                }
            )

    # Error clusters: > 10 errors within a 5-minute window
    error_ts: Dict[str, List[datetime]] = defaultdict(list)
    for l in valid_logs:
        if 400 <= l["status_code"] <= 599:
            error_ts[l["endpoint"]].append(l["timestamp"])
    for ep, ts_list in error_ts.items():
        ts_list.sort()
        for t, count in sliding_window_counts(ts_list, ERROR_CLUSTER_WINDOW_MINUTES):
            if count >= ERROR_CLUSTER_THRESHOLD:
                anomalies.append(
                    {
                        "type": "error_cluster",
                        "endpoint": ep,
                        "time_window": f"{(t - timedelta_minutes(ERROR_CLUSTER_WINDOW_MINUTES)).strftime('%H:%M')}-{t.strftime('%H:%M')}",
                        "error_count": int(count),
                        "severity": "critical" if count >= ERROR_CLUSTER_THRESHOLD * 2 else "high",
                    }
                )
                break

    # Unusual user behavior: single user > 50% of total requests
    total = len(valid_logs)
    user_counts = Counter(l["user_id"] for l in valid_logs)
    if total > 0:
        user_id, cnt = user_counts.most_common(1)[0]
        share = cnt / total
        if share > UNUSUAL_USER_SHARE_THRESHOLD:
            anomalies.append(
                {
                    "type": "unusual_user_behavior",
                    "user_id": user_id,
                    "share_percentage": round(share * 100, 3),
                    "severity": "high" if share > 0.7 else "medium",
                }
            )

    return anomalies


def analyze_api_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Validate and normalize logs
    valid_logs: List[Dict[str, Any]] = []
    for entry in logs or []:
        v = validate_log_entry(entry)
        if v:
            valid_logs.append(v)

    # Core outputs
    summary = _calc_summary(valid_logs)
    endpoint_stats = _calc_endpoint_stats(valid_logs)
    performance_issues = _detect_performance_issues(endpoint_stats)
    recommendations = _recommendations(summary, endpoint_stats)
    hourly_distribution = _hourly_distribution(valid_logs)
    top_users_by_requests = _top_users(valid_logs, 5)

    # Advanced features
    cost_analysis = _cost_analysis(valid_logs, endpoint_stats)
    anomalies = _anomalies(valid_logs, endpoint_stats)

    return {
        "summary": summary,
        "endpoint_stats": endpoint_stats,
        "performance_issues": performance_issues,
        "recommendations": recommendations,
        "hourly_distribution": hourly_distribution,
        "top_users_by_requests": top_users_by_requests,
        "cost_analysis": cost_analysis,
        "anomalies": anomalies,
    }


# Simple CLI usage to test with a JSON file:
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 2:
        print("Usage: python function.py <path_to_json_logs>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = analyze_api_logs(data)
    print(json.dumps(result, indent=2))
