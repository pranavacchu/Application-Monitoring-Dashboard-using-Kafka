import requests
import random
import time
import threading
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoints
BASE_URL = "http://localhost:5000"
ENDPOINTS = [
    "/api/users",
    "/api/products",
    "/api/orders"
]

# Test data
USERS = [
    {"username": f"user{i}", "email": f"user{i}@example.com"} for i in range(1, 6)
]

PRODUCTS = [
    {"name": f"Product {i}", "price": round(random.uniform(10, 100), 2)} for i in range(1, 6)
]

def make_request(endpoint, method="GET", data=None):
    """Make an API request and log the response"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        duration = time.time() - start_time
        logger.info(f"{method} {endpoint} - Status: {response.status_code} - Duration: {duration:.2f}s")
        return response.status_code, duration
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error making request to {endpoint}: {str(e)} - Duration: {duration:.2f}s")
        return None, duration

def simulate_user_workload():
    """Simulate user-related API calls"""
    while True:
        # Create user
        user_data = random.choice(USERS)
        status, duration = make_request("/api/users", "POST", user_data)
        
        # Get users
        status, duration = make_request("/api/users")
        
        # Simulate random delays
        time.sleep(random.uniform(0.5, 2))

def simulate_product_workload():
    """Simulate product-related API calls"""
    while True:
        # Create product
        product_data = random.choice(PRODUCTS)
        status, duration = make_request("/api/products", "POST", product_data)
        
        # Get products
        status, duration = make_request("/api/products")
        
        # Simulate random delays
        time.sleep(random.uniform(0.5, 2))

def simulate_order_workload():
    """Simulate order-related API calls"""
    while True:
        # Create order
        order_data = {
            "user_id": random.randint(1, 5),
            "product_id": random.randint(1, 5),
            "quantity": random.randint(1, 10)
        }
        status, duration = make_request("/api/orders", "POST", order_data)
        
        # Get orders
        status, duration = make_request("/api/orders")
        
        # Simulate random delays
        time.sleep(random.uniform(0.5, 2))

def simulate_error_workload():
    """Simulate error conditions"""
    error_patterns = [
        # Invalid data
        {"invalid": "data"},
        # Missing required fields
        {},
        # Wrong data types
        {"username": 123, "email": 456},
        # SQL injection attempt
        {"username": "admin' --", "email": "test@example.com"},
        # Very long input
        {"username": "a" * 1000, "email": "test@example.com"}
    ]
    
    while True:
        for endpoint in ["/api/users", "/api/products", "/api/orders"]:
            # Test each error pattern
            for error_data in error_patterns:
                status, duration = make_request(endpoint, "POST", error_data)
                time.sleep(random.uniform(0.5, 1))
        
        time.sleep(random.uniform(1, 3))

def simulate_slow_requests():
    """Simulate slow requests to test response time monitoring"""
    while True:
        # Simulate slow database query
        time.sleep(random.uniform(2, 5))
        status, duration = make_request("/api/users")
        
        # Simulate high CPU usage
        time.sleep(random.uniform(1, 3))
        status, duration = make_request("/api/products")
        
        time.sleep(random.uniform(2, 4))

def simulate_high_load():
    """Simulate high load conditions"""
    while True:
        # Burst of requests
        for _ in range(10):
            status, duration = make_request("/api/users")
            status, duration = make_request("/api/products")
            status, duration = make_request("/api/orders")
        
        time.sleep(random.uniform(1, 2))

def main():
    """Start all workload simulations"""
    logger.info("Starting workload simulation...")
    
    # Create threads for each workload type
    threads = [
        threading.Thread(target=simulate_user_workload),
        threading.Thread(target=simulate_product_workload),
        threading.Thread(target=simulate_order_workload),
        threading.Thread(target=simulate_error_workload),
        threading.Thread(target=simulate_slow_requests),
        threading.Thread(target=simulate_high_load)
    ]
    
    # Start all threads
    for thread in threads:
        thread.daemon = True
        thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping workload simulation...")

if __name__ == "__main__":
    main() 