# Rival.io - Software Development Internship
## Take-Home Coding Assignment

---

## 📋 Assignment Overview

**Deadline:** 72 hours from receipt
**Language:** Choose ONE: Python, JavaScript, or Lua
**Submission Method:** GitHub repository (public or private with access granted to: sabir@rival.io)

---

## 🎯 The Challenge

You're building a **serverless function** for Rival.io's marketplace that helps developers **analyze and optimize their API usage patterns**.

This assignment tests your ability to:
- Process and analyze complex data structures
- Write production-quality code
- Handle edge cases and errors gracefully
- Think about performance and scalability
- Document your work professionally

---

## Part 1: Core Function (40 points)

### Requirements

Build a function called `analyze_api_logs` that processes API call logs and generates comprehensive analytics.

### Input Format

Your function receives a JSON array of API call logs:

```json
[
  {
    "timestamp": "2025-01-15T10:30:00Z",
    "endpoint": "/api/users",
    "method": "GET",
    "response_time_ms": 245,
    "status_code": 200,
    "user_id": "user_123",
    "request_size_bytes": 512,
    "response_size_bytes": 2048
  },
  {
    "timestamp": "2025-01-15T10:31:15Z",
    "endpoint": "/api/payments",
    "method": "POST",
    "response_time_ms": 1450,
    "status_code": 500,
    "user_id": "user_456",
    "request_size_bytes": 1024,
    "response_size_bytes": 256
  }
  // ... more logs
]
```

### Expected Output Format

```json
{
  "summary": {
    "total_requests": 1000,
    "time_range": {
      "start": "2025-01-15T10:00:00Z",
      "end": "2025-01-15T11:00:00Z"
    },
    "avg_response_time_ms": 189.5,
    "error_rate_percentage": 2.3
  },
  "endpoint_stats": [
    {
      "endpoint": "/api/users",
      "request_count": 450,
      "avg_response_time_ms": 210,
      "slowest_request_ms": 890,
      "fastest_request_ms": 45,
      "error_count": 5,
      "most_common_status": 200
    }
  ],
  "performance_issues": [
    {
      "type": "slow_endpoint",
      "endpoint": "/api/reports",
      "avg_response_time_ms": 1250,
      "threshold_ms": 500,
      "severity": "high"
    },
    {
      "type": "high_error_rate",
      "endpoint": "/api/payments",
      "error_rate_percentage": 15.5,
      "severity": "critical"
    }
  ],
  "recommendations": [
    "Consider caching for /api/users (450 requests, 89% cache-hit potential)",
    "Investigate /api/reports performance (avg 1250ms exceeds 500ms threshold)",
    "Alert: /api/payments has 15.5% error rate"
  ],
  "hourly_distribution": {
    "10:00": 234,
    "11:00": 456
  },
  "top_users_by_requests": [
    {"user_id": "user_123", "request_count": 89},
    {"user_id": "user_456", "request_count": 67}
  ]
}
```

### Core Requirements

1. **Handle large datasets efficiently** - Your function should process 10,000+ log entries
2. **Performance issue detection:**
   - Response time > 500ms = "medium" severity
   - Response time > 1000ms = "high" severity
   - Response time > 2000ms = "critical" severity
3. **Error rate detection:**
   - Error rate > 5% = "medium" severity
   - Error rate > 10% = "high" severity
   - Error rate > 15% = "critical" severity
4. **Generate actionable recommendations** based on the data patterns
5. **Handle edge cases:**
   - Empty log arrays
   - Malformed/missing fields
   - Invalid timestamps
   - Negative numbers
   - Single log entry
6. **Calculate accurate statistics** for each endpoint
7. **Top 5 users** by request count
8. **Hourly distribution** of requests

---

## Part 2: Advanced Features (30 points)

**Choose and implement TWO of the following features:**

### Option A: Cost Estimation Engine

Calculate estimated compute costs for running these API calls in a serverless environment.

**Requirements:**
- Cost per request: $0.0001
- Cost per millisecond execution: $0.000002
- Memory cost estimation (based on response_size_bytes):
  - 0-1KB = $0.00001
  - 1-10KB = $0.00005
  - 10KB+ = $0.0001

**Output addition:**
```json
{
  "cost_analysis": {
    "total_cost_usd": 12.45,
    "cost_breakdown": {
      "request_costs": 1.00,
      "execution_costs": 8.50,
      "memory_costs": 2.95
    },
    "cost_by_endpoint": [
      {
        "endpoint": "/api/users",
        "total_cost": 5.67,
        "cost_per_request": 0.0126
      }
    ],
    "optimization_potential_usd": 3.45
  }
}
```

### Option B: Anomaly Detection

Identify unusual patterns in API usage that might indicate issues or attacks.

**Detect:**
- Request spikes (> 3× average rate within a 5-minute window)
- Response time degradation (> 2× normal average for an endpoint)
- Error clusters (> 10 errors within a 5-minute window)
- Unusual user behavior (single user > 50% of total requests)

**Output addition:**
```json
{
  "anomalies": [
    {
      "type": "request_spike",
      "endpoint": "/api/search",
      "timestamp": "2025-01-15T10:45:00Z",
      "normal_rate": 50,
      "actual_rate": 180,
      "severity": "high"
    },
    {
      "type": "error_cluster",
      "endpoint": "/api/payments",
      "time_window": "10:30-10:35",
      "error_count": 23,
      "severity": "critical"
    }
  ]
}
```

### Option C: Rate Limiting Analysis

Given rate limit rules, identify which users or endpoints violated the limits.

**Input configuration:**
```json
{
  "rate_limits": {
    "per_user": {
      "requests_per_minute": 100,
      "requests_per_hour": 1000
    },
    "per_endpoint": {
      "requests_per_minute": 500,
      "requests_per_hour": 5000
    }
  }
}
```

**Output addition:**
```json
{
  "rate_limit_violations": {
    "user_violations": [
      {
        "user_id": "user_123",
        "violation_type": "per_minute",
        "limit": 100,
        "actual": 156,
        "timestamp": "2025-01-15T10:30:00Z"
      }
    ],
    "endpoint_violations": [
      {
        "endpoint": "/api/search",
        "violation_type": "per_hour",
        "limit": 5000,
        "actual": 5340
      }
    ],
    "total_violations": 12
  }
}
```

### Option D: Caching Opportunity Analysis

Identify endpoints that would benefit most from caching implementation.

**Analysis criteria:**
- High request frequency (> 100 requests)
- Majority are GET requests (> 80%)
- Low error rate (< 2%)
- Consistent response patterns

**Output addition:**
```json
{
  "caching_opportunities": [
    {
      "endpoint": "/api/users",
      "potential_cache_hit_rate": 89,
      "current_requests": 450,
      "potential_requests_saved": 400,
      "estimated_cost_savings_usd": 2.34,
      "recommended_ttl_minutes": 15,
      "recommendation_confidence": "high"
    }
  ],
  "total_potential_savings": {
    "requests_eliminated": 1200,
    "cost_savings_usd": 8.90,
    "performance_improvement_ms": 1850
  }
}
```

---

## Part 3: Production Readiness (30 points)

### A) Testing (15 points)

Write comprehensive tests covering:

1. **Unit tests** for core logic
2. **Edge cases:**
   - Empty input array
   - Single log entry
   - Malformed data (missing fields, invalid types)
   - Invalid timestamps
   - Negative values
3. **Performance test:** Process 10,000+ logs in under 2 seconds
4. **Integration tests** with the sample datasets we provide

**Test coverage expected:** Minimum 80%

### B) Documentation (10 points)

Your repository must include:

1. **README.md** with:
   - Project overview
   - Setup instructions (dependencies, installation)
   - How to run the function
   - How to run tests
   - Usage examples
   - Time and space complexity analysis

2. **DESIGN.md** answering:
   - Which two advanced features did you choose and why?
   - What trade-offs did you make in your implementation?
   - How would you scale this to handle 1 million+ logs?
   - What would you improve given more time?
   - Approximate time spent on this assignment (be honest)

3. **Code documentation:**
   - Function-level docstrings
   - Inline comments for complex logic
   - Type hints (Python) or JSDoc (JavaScript)

### C) Code Quality (5 points)

- Clean, readable code following language conventions
  - Python: PEP 8
  - JavaScript: ESLint/Airbnb style
  - Lua: Lua Style Guide
- Proper error handling with meaningful messages
- Input validation
- No hardcoded values (use constants/configuration)
- Modular design (separate concerns)
- Efficient algorithms (avoid unnecessary loops)

---

## 📦 Repository Structure

Your GitHub repository should follow this structure:

```
your-name-rival-assignment/
├── README.md                     # Main documentation
├── DESIGN.md                     # Design decisions & approach
├── function.py / main.js / main.lua   # Main function
├── config.py / config.js / config.lua # Configuration
├── utils.py / utils.js / utils.lua    # Helper functions
├── tests/
│   ├── test_function.py/js/lua   # Test files
│   ├── test_edge_cases.py/js/lua
│   └── test_data/
│       ├── sample_small.json     # You create these
│       ├── sample_medium.json
│       └── sample_large.json
├── requirements.txt              # Python dependencies
├── package.json                  # JavaScript dependencies
└── .gitignore
```

---

## 🎯 Evaluation Criteria

| Criterion | Points | What We Evaluate |
|-----------|--------|------------------|
| **Core Function Correctness** | 25 | Accuracy, completeness, logic |
| **Edge Case Handling** | 15 | Robustness, validation, error handling |
| **Advanced Features** | 30 | Problem-solving, algorithm choice, implementation quality |
| **Testing** | 15 | Coverage, edge cases, performance tests |
| **Documentation** | 10 | Clarity, completeness, design rationale |
| **Code Quality** | 5 | Readability, structure, best practices |
| **Bonus Points** | +10 | Exceptional quality, extra features, creativity |
| **Total** | **100** | |

**Scoring Guide:**
- **60-74:** Pass - Adequate implementation
- **75-84:** Strong - Well-executed solution
- **85-100:** Exceptional - Outstanding work

---

## 📝 Submission Guidelines

### What to Submit

1. **GitHub Repository Link**
   - Make it public, OR
   - Make it private and grant access to: `sabir@rival.io`

2. **Email to:** sabir@rival.io
   **Subject:** Internship Assignment Submission - [Your Name]

3. **Email should include:**
   - Your full name
   - GitHub repository link
   - Brief note on your chosen advanced features
   - Any challenges you faced (optional)

### Deadline

**72 hours** from when you receive this assignment.

If you need an extension due to valid reasons, email us **before** the deadline.

---

## ⚠️ Important Notes

### Academic Integrity

- You may use documentation, Stack Overflow, and AI tools (ChatGPT, Claude, GitHub Copilot, etc.)
- **However:** You must understand every line of code you submit
- You'll be asked to explain your solution in a follow-up interview
- We value problem-solving approach over perfect code

### What Happens Next

1. We'll review your submission within 3-4 business days
2. Shortlisted candidates will be invited for a technical interview
3. In the interview, you'll:
   - Walk through your code
   - Explain design decisions
   - Potentially do some live coding
   - Discuss improvements and alternatives

### Questions?

If you have questions about the assignment:
- Try to make reasonable assumptions first (document them in DESIGN.md)
- If truly blocked, email: sabir@rival.io
- We'll respond within 24 hours

---

## 💡 Tips for Success

1. **Start simple** - Get the core function working first, then add features
2. **Test as you go** - Don't wait until the end to write tests
3. **Commit frequently** - We like to see your thought process
4. **Focus on clarity** - Readable code > clever code
5. **Handle errors gracefully** - Don't let the function crash
6. **Document your decisions** - Especially in DESIGN.md
7. **Manage your time** - This should take 6-12 hours, don't overthink it

---

## 🚀 Good Luck!

We're excited to see your solution! This assignment reflects the kind of real-world problems you'll solve at Rival.io.

Remember: We're not looking for perfection. We're looking for:
- Clear thinking
- Clean code
- Problem-solving ability
- Attention to detail
- Communication skills

**Questions?** Email sabir@rival.io

**Ready to start?** Clone this assignment and start coding!

---

**Rival.io** - Building the future of serverless computing
