from kafka import KafkaConsumer
import json
import requests
import logging
import time
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get Kafka broker from environment variable or use default
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'logs',
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='log-consumer-group'
)

# Loki endpoint
LOKI_URL = "http://loki:3100/loki/api/v1/push"

def send_to_loki(log_data):
    """Send log data to Loki"""
    try:
        # Format timestamp to nanoseconds
        timestamp = int(datetime.now().timestamp() * 1000000000)
        
        # Format log entry for Loki
        labels = {
            "job": "api-server",
            "level": log_data.get('level', 'INFO'),
            "endpoint": log_data.get('endpoint', 'unknown'),
            "status_code": str(log_data.get('status_code', 200))
        }
        
        # Create Loki payload
        payload = {
            "streams": [{
                "stream": labels,
                "values": [[
                    str(timestamp),
                    json.dumps({
                        "message": log_data.get('message', ''),
                        "timestamp": log_data.get('timestamp', ''),
                        "level": log_data.get('level', 'INFO'),
                        "endpoint": log_data.get('endpoint', 'unknown'),
                        "status_code": log_data.get('status_code', 200)
                    })
                ]]
            }]
        }
        
        logger.info(f"Sending to Loki: {json.dumps(payload)}")
        
        # Send to Loki
        response = requests.post(
            LOKI_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code != 204:
            logger.error(f"Failed to send log to Loki: {response.status_code} - {response.text}")
        else:
            logger.info("Successfully sent log to Loki")
    except Exception as e:
        logger.error(f"Error sending log to Loki: {str(e)}")

def main():
    logger.info(f"Starting log consumer... Connecting to Kafka at {KAFKA_BROKER}")
    try:
        for message in consumer:
            log_data = message.value
            logger.info(f"Received log from Kafka: {log_data}")
            send_to_loki(log_data)
    except Exception as e:
        logger.error(f"Error in log consumer: {str(e)}")
        time.sleep(5)  # Wait before retrying
        main()  # Restart consumer

if __name__ == "__main__":
    main() 