from flask import Flask, request, jsonify
from kafka import KafkaProducer
import mysql.connector
import json
import os
import time
from prometheus_client import Counter, Histogram, start_http_server
import logging
import re
import random

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])

# Initialize Kafka producer with retry logic
def init_kafka_producer():
    max_retries = 5
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=os.getenv('KAFKA_BROKER'),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3
            )
            # Test the connection by sending a test message
            producer.send('test_topic', {'test': 'connection'})
            producer.flush(timeout=5)
            return producer
        except Exception as e:
            if attempt < max_retries - 1:
                logging.warning(f"Failed to connect to Kafka (attempt {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to connect to Kafka after {max_retries} attempts: {str(e)}")
                raise

# Initialize Kafka producer
try:
    producer = init_kafka_producer()
except Exception as e:
    logging.error(f"Failed to initialize Kafka producer: {str(e)}")
    producer = None

# MySQL connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

# Initialize database schema
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            level VARCHAR(10),
            message TEXT,
            endpoint VARCHAR(255),
            status_code INT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.path).observe(latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    
    # Log to Kafka if producer is available
    if producer is not None:
        try:
            log_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'level': 'ERROR' if response.status_code >= 400 else 'INFO',
                'message': f"{request.method} {request.path} - {response.status_code}",
                'endpoint': request.path,
                'status_code': response.status_code,
                'job': 'api-server'  # Add job label for Loki
            }
            producer.send('logs', value=log_data)
        except Exception as e:
            logging.error(f"Failed to send log to Kafka: {str(e)}")
    
    return response

def validate_user_data(data):
    if not data:
        return False, "Missing data"
    if not isinstance(data, dict):
        return False, "Invalid data format"
    if not data.get('username') or not data.get('email'):
        return False, "Missing required fields"
    if not isinstance(data['username'], str) or not isinstance(data['email'], str):
        return False, "Invalid data types"
    if len(data['username']) > 100:
        return False, "Username too long"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        return False, "Invalid email format"
    if any(char in data['username'] for char in ["'", '"', ';', '--']):
        return False, "Invalid characters in username"
    return True, None

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"message": "List of users"})

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        is_valid, error_message = validate_user_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Simulate database error randomly
        if random.random() < 0.1:  # 10% chance of error
            raise Exception("Database connection error")
            
        return jsonify({"message": "User created"}), 201
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify({"message": "List of products"})

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('price'):
            return jsonify({"error": "Missing required fields"}), 400
        if not isinstance(data['name'], str) or not isinstance(data['price'], (int, float)):
            return jsonify({"error": "Invalid data types"}), 400
        if len(data['name']) > 100:
            return jsonify({"error": "Product name too long"}), 400
            
        # Simulate database error randomly
        if random.random() < 0.1:  # 10% chance of error
            raise Exception("Database connection error")
            
        return jsonify({"message": "Product created"}), 201
    except Exception as e:
        logging.error(f"Error creating product: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    return jsonify({"message": "List of orders"})

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        if not data or not data.get('user_id') or not data.get('product_id') or not data.get('quantity'):
            return jsonify({"error": "Missing required fields"}), 400
        if not all(isinstance(data[key], int) for key in ['user_id', 'product_id', 'quantity']):
            return jsonify({"error": "Invalid data types"}), 400
        if data['quantity'] <= 0:
            return jsonify({"error": "Invalid quantity"}), 400
            
        # Simulate database error randomly
        if random.random() < 0.1:  # 10% chance of error
            raise Exception("Database connection error")
            
        return jsonify({"message": "Order created"}), 201
    except Exception as e:
        logging.error(f"Error creating order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    init_db()
    start_http_server(8000)  # Start Prometheus metrics server
    app.run(host='0.0.0.0', port=5000) 