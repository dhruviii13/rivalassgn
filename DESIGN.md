# DESIGN

## Advanced Features Chosen
- Option A: Cost Estimation Engine
- Option B: Anomaly Detection

### Why these two?
- Cost Estimation gives actionable business metrics and optimization potential tied directly to runtime and payload sizes.
- Anomaly Detection highlights operational risks (spikes, degradations, error clusters, unusual user behavior) useful for incident response.

## Core Approach
- Single-pass aggregations via dictionaries and counters.
- UTC timestamp parsing; normalization in validation step.
- Endpoint stats: counts, avg/slowest/fastest response times, error counts, most common status.
- Performance issues: severity computed from configured thresholds.
- Recommendations: focus on slow endpoints and high error rates.
- Hourly distribution: HH:00 buckets in UTC.
- Top users: Counter.most_common(5).

## Cost Estimation
- Per-request: constant cost.
- Execution cost: proportional to response_time_ms.
- Memory cost: bracketed by response_size_bytes.
- Endpoint cost breakdown computed incrementally.
- Optimization potential: estimated savings from reducing avg response time to medium threshold across slow endpoints.

## Anomaly Detection
- Request spikes: two-pointer sliding window over per-endpoint timestamps with 5-minute window; compare to average window rate.
- Response time degradation: recent 10% vs overall average per endpoint.
- Error clusters: errors per endpoint in 5-minute window crossing threshold.
- Unusual user behavior: single user share exceeding 50%.

## Trade-offs
- Sliding window uses per-endpoint lists for timestamps; simple and efficient for 10k–100k. For millions, may prefer stream processing with fixed-interval bins to reduce memory.
- Response degradation uses last 10% heuristic; configurable in future for more precision (e.g., EWMA).
- Optimization potential is a heuristic; accurate savings need real workload modeling.

## Scaling to 1M+ Logs
- Use streaming/iterative processing: process logs in chunks, maintain running aggregates (counts, sums, counters) to avoid holding all logs.
- For anomalies:
  - Request spikes/error clusters: bin counts per minute and per endpoint; apply sliding windows on bins, not raw timestamps.
  - Response time degradation: keep rolling stats (mean, variance) per endpoint using online algorithms.
- Persist intermediate aggregates (e.g., sqlite/duckdb) for memory safety.
- Parallelize by endpoint/user partitions; aggregate partial results.
- Consider Python optimizations: PyPy, C extensions for hot paths, or NumPy for vectorized bin operations.

## Improvements with More Time
- Configurable anomaly parameters per endpoint.
- Add percentile metrics (p95/p99) for response times.
- Cache opportunity analysis (Option D) and rate limiting analysis (Option C).
- Better recommendations using correlation between method types and errors.
- Output schema validation and JSON schema for inputs/outputs.

## Time Spent
- Implementation: ~2.5 hours
- Tests and performance: ~1 hour
- Documentation: ~0.5 hour
