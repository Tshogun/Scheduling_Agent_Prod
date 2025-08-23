
# scripts/quick-test.py
# Python script for quick API testing
import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_ping():
    response = requests.get(f"{BASE_URL}/api/v1/ping")
    print(f"Ping: {response.json()}")

def test_completion():
    payload = {
        "prompt": "Write a short poem about coding",
        "model": "gpt-3.5-turbo",
        "max_tokens": 100
    }
    response = requests.post(f"{BASE_URL}/api/v1/completion", json=payload)
    print(f"Completion: {response.json()}")

def test_optimization():
    payload = {
        "problem_type": "vehicle_routing",
        "constraints_json": json.dumps({"vehicles": 3, "locations": 10}),
        "objectives_json": json.dumps({"minimize": "total_distance"}),
        "timeout_seconds": 60
    }
    
    # Start optimization
    response = requests.post(f"{BASE_URL}/api/v1/optimize", json=payload)
    result = response.json()
    print(f"Optimization started: {result}")
    
    if "job_id" in result:
        job_id = result["job_id"]
        
        # Check status a few times
        for i in range(3):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/v1/job/{job_id}")
            status = status_response.json()
            print(f"Job status (check {i+1}): {status}")
            
            if status.get("status") in ["completed", "failed"]:
                break

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    try:
        test_ping()
        print()
        
        test_completion()
        print()
        
        test_optimization()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to services. Make sure they're running!")