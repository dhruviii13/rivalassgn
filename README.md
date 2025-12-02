# Rival.io Internship Assignment – Python Implementation

## Overview
This repository implements analyze_api_logs with:
- Core analytics (summary, endpoint stats, performance issues, recommendations, hourly distribution, top users).
- Option A: Cost Estimation.
- Option B: Anomaly Detection.

## Setup
- Create and activate venv (already prepared by you).
- Install dependencies:
- Python
pip install -r requirements.txt

## Usage
- Python
python function.py tests/test_data/sample_small.json

Output is printed as JSON including keys:
summary, endpoint_stats, performance_issues, recommendations, hourly_distribution, top_users_by_requests, cost_analysis, anomalies.

## Tests
- Run all tests:
- Python
python -m pytest -q

- Run performance-only:
- Python
python -m pytest -q -k performance

### Test Coverage
- Unit tests: core logic (summary, endpoint stats, distributions, top users).
- Edge cases: empty input, single entry, malformed/missing fields, invalid timestamps, negative values, error rate severity.
- Performance: 12,000 logs processed under 2 seconds on typical laptop.

## Integration Data
Sample datasets for manual runs are in tests/test_data/:
- sample_small.json (added)
- sample_medium.json (planned)
- sample_large.json (planned)

## Design Notes (Short)
- Single-pass aggregations and counters ensure $O(n)$ time over logs.
- Sliding windows use two-pointers for anomaly detection to avoid $O(n^2)$.
- Memory bounded by unique endpoints/users: $O(e + u)$.

## Complexity
- Time: $O(n)$ for core analytics, $O(n)$ for anomalies via two-pointer sliding windows.
- Space: $O(e + u)$ where $e$ = endpoints, $u$ = users.

## Notes
- Skips invalid or negative fields safely.
- Timestamps parsed as UTC; hourly distribution uses HH:00 (UTC).
- Cost model follows assignment brackets and rates.
