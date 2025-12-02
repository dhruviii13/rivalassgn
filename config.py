"""
Configuration constants for analysis and advanced features.
"""

from typing import Final

# Performance severity thresholds (ms)
SEVERITY_THRESHOLDS_MS: Final = {
    "medium": 500,
    "high": 1000,
    "critical": 2000,
}

# Error rate severity thresholds (%)
ERROR_RATE_THRESHOLDS_PERCENT: Final = {
    "medium": 5.0,
    "high": 10.0,
    "critical": 15.0,
}

# Cost model (USD)
COST_PER_REQUEST_USD: Final = 0.0001
COST_PER_MS_EXECUTION_USD: Final = 0.000002

# Memory cost by response size (bytes)
# 0-1KB: $0.00001, 1-10KB: $0.00005, 10KB+: $0.0001
MEMORY_COST_BRACKETS: Final = [
    (0, 1024, 0.00001),
    (1024, 10 * 1024, 0.00005),
    (10 * 1024, float("inf"), 0.0001),
]

# Anomaly Detection settings
REQUEST_SPIKE_WINDOW_MINUTES: Final = 5
REQUEST_SPIKE_MULTIPLIER: Final = 3.0

RESPONSE_DEGRADATION_MULTIPLIER: Final = 2.0

ERROR_CLUSTER_WINDOW_MINUTES: Final = 5
ERROR_CLUSTER_THRESHOLD: Final = 10

UNUSUAL_USER_SHARE_THRESHOLD: Final = 0.5  # 50%

# General defaults
DEFAULT_SLOW_ENDPOINT_THRESHOLD_MS: Final = SEVERITY_THRESHOLDS_MS["medium"]

# Data validation: fields we expect
REQUIRED_FIELDS: Final = [
    "timestamp",
    "endpoint",
    "method",
    "response_time_ms",
    "status_code",
    "user_id",
    "request_size_bytes",
    "response_size_bytes",
]
