import json
import random
from datetime import datetime, timedelta

def generate_logs(num_entries=10000):
    start_time = datetime.strptime("2025-01-15T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
    
    # Configuration for different endpoints
    endpoints_config = {
        "/api/users": {
            "method": "GET",
            "resp_time_range": (100, 200),
            "req_size_range": (300, 400),
            "resp_size_range": (1500, 1600),
            "error_rate": 0.05
        },
        "/api/search": {
            "method": "GET",
            "resp_time_range": (450, 550),
            "req_size_range": (400, 480),
            "resp_size_range": (2000, 2150),
            "error_rate": 0.02
        },
        "/api/payments": {
            "method": "POST",
            "resp_time_range": (800, 1100),
            "req_size_range": (1024, 1024),
            "resp_size_range": (250, 310),
            "error_rate": 0.3
        },
        "/api/reports": {
            "method": "GET",
            "resp_time_range": (1900, 2200),
            "req_size_range": (500, 600),
            "resp_size_range": (5000, 6000),
            "error_rate": 0.01
        }
    }

    endpoints_list = list(endpoints_config.keys())
    weights = [0.4, 0.2, 0.2, 0.2] # Distribution probability
    logs = []

    print(f"Generating {num_entries} logs...")

    for i in range(num_entries):
        # Timestamp increments by 1 second per log
        current_time = start_time + timedelta(seconds=i)
        timestamp_str = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # User ID cycles from u1 to u10
        user_id = f"u{(i % 10) + 1}"
        
        # Select endpoint based on weights
        endpoint = random.choices(endpoints_list, weights=weights, k=1)[0]
        config = endpoints_config[endpoint]
        
        # Determine status code
        if random.random() < config["error_rate"]:
            status_code = 500
        else:
            status_code = 200
            
        log_entry = {
            "timestamp": timestamp_str,
            "endpoint": endpoint,
            "method": config["method"],
            "response_time_ms": random.randint(*config["resp_time_range"]),
            "status_code": status_code,
            "user_id": user_id,
            "request_size_bytes": random.randint(*config["req_size_range"]),
            "response_size_bytes": random.randint(*config["resp_size_range"])
        }
        
        logs.append(log_entry)

    # Write to file
    output_file = "sample_large.json"
    with open(output_file, "w") as f:
        json.dump(logs, f, indent=2)
    
    print(f"Success! {num_entries} logs saved to {output_file}")

if __name__ == "__main__":
    generate_logs()