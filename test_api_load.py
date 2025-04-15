"""
Load test script for IPL API
This script conducts basic load testing on the API endpoints to ensure they remain responsive
under load.
"""

import requests
import time
import concurrent.futures
import argparse
import sys
import statistics

BASE_URL = "http://localhost:8080"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword"
}

# Endpoints to test with parameters
ENDPOINTS = [
    ("/api/teams-played-ipl", {}),
    ("/api/team1-vs-team2", {"team1": "Mumbai Indians", "team2": "Chennai Super Kings"}),
    ("/api/record-against-all-teams", {"team": "Royal Challengers Bangalore"}),
    ("/api/record-against-each-team", {"team": "Kolkata Knight Riders"}),
    ("/api/batsman-record", {"batsman": "MS Dhoni"}),
    ("/api/bowling-record", {"bowler": "RA Jadeja"})
]

def login_and_get_session():
    """Log in and return the session with cookies"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", data=TEST_USER)
    if response.status_code != 200:
        print(f"Login failed with status code {response.status_code}")
        sys.exit(1)
    return session

def test_endpoint(session, endpoint, params, request_id=None):
    """Test a single endpoint and return response time"""
    start_time = time.time()
    url = f"{BASE_URL}{endpoint}"
    try:
        response = session.get(url, params=params, timeout=10)
        elapsed = time.time() - start_time
        status = response.status_code
        return {
            "request_id": request_id,
            "endpoint": endpoint,
            "status_code": status,
            "response_time": elapsed,
            "success": status == 200
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "request_id": request_id,
            "endpoint": endpoint,
            "status_code": 0,
            "response_time": elapsed,
            "success": False,
            "error": str(e)
        }

def run_load_test(num_requests, concurrency):
    """Run load test with specified concurrency and number of requests"""
    print(f"Starting load test with {num_requests} total requests, {concurrency} concurrent requests")
    
    # Login and get session with cookies
    session = login_and_get_session()
    
    # Prepare the requests
    tasks = []
    for i in range(num_requests):
        # Cycle through endpoints
        endpoint, params = ENDPOINTS[i % len(ENDPOINTS)]
        tasks.append((session, endpoint, params, i+1))
    
    # Execute requests with ThreadPoolExecutor for concurrency
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(test_endpoint, *task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            if result["success"]:
                print(f"Request {result['request_id']} to {result['endpoint']} completed in {result['response_time']:.2f}s")
            else:
                print(f"Request {result['request_id']} to {result['endpoint']} failed: {result.get('error', f'Status code {result['status_code']}')}")
    
    total_time = time.time() - start_time
    
    # Analyze results
    success_count = sum(1 for r in results if r["success"])
    response_times = [r["response_time"] for r in results if r["success"]]
    
    if response_times:
        avg_response = statistics.mean(response_times)
        median_response = statistics.median(response_times)
        max_response = max(response_times)
        min_response = min(response_times)
    else:
        avg_response = median_response = max_response = min_response = 0
    
    # Print summary
    print("\n===== Load Test Results =====")
    print(f"Total requests: {num_requests}")
    print(f"Successful requests: {success_count} ({success_count/num_requests*100:.1f}%)")
    print(f"Failed requests: {num_requests - success_count}")
    print(f"Total test time: {total_time:.2f}s")
    print(f"Requests per second: {num_requests/total_time:.2f}")
    print("\nResponse time (successful requests):")
    print(f"  Average: {avg_response:.2f}s")
    print(f"  Median: {median_response:.2f}s")
    print(f"  Min: {min_response:.2f}s")
    print(f"  Max: {max_response:.2f}s")
    
    # Group results by endpoint
    endpoint_stats = {}
    for r in results:
        ep = r["endpoint"]
        if ep not in endpoint_stats:
            endpoint_stats[ep] = {
                "total": 0,
                "success": 0,
                "times": []
            }
        endpoint_stats[ep]["total"] += 1
        if r["success"]:
            endpoint_stats[ep]["success"] += 1
            endpoint_stats[ep]["times"].append(r["response_time"])
    
    print("\nEndpoint Performance:")
    for endpoint, stats in endpoint_stats.items():
        success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
        avg_time = statistics.mean(stats["times"]) if stats["times"] else 0
        print(f"  {endpoint}: {success_rate:.1f}% success, avg {avg_time:.2f}s")
    
    return success_count == num_requests

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load test the IPL API')
    parser.add_argument('-n', '--requests', type=int, default=10, help='Total number of requests')
    parser.add_argument('-c', '--concurrency', type=int, default=2, help='Number of concurrent requests')
    args = parser.parse_args()
    
    # Run load test
    success = run_load_test(args.requests, args.concurrency)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)