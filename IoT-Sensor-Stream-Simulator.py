import boto3
import json
import random
import time

# Initialize Kinesis client
kinesis_client = boto3.client('kinesis')

# Number of records to simulate
i = 500

def get_sensor_data():
    """
    Simulates sensor data by generating random values for sensor ID, temperature, humidity, and a timestamp.
    
    Returns:
    - dict: A dictionary containing randomly generated sensor data.
        - 'sensor_id' (int): Randomly generated sensor ID between 1000 and 9999.
        - 'temperature' (float): Randomly generated temperature between 20.0°C and 35.0°C, rounded to 2 decimal places.
        - 'humidity' (float): Randomly generated humidity between 30.0% and 80.0%, rounded to 2 decimal places.
        - 'timestamp' (int): The current Unix timestamp (seconds since the epoch).
    """
    return {
        'sensor_id': random.randint(1000, 9999),
        'temperature': round(random.uniform(20.0, 35.0), 2),
        'humidity': round(random.uniform(30.0, 80.0), 2),
        'timestamp': int(time.time())
    }

while i>0:
    data = json.dumps(get_sensor_data())
    kinesis_client.put_record(
        StreamName='IoT-Sensor-Stream',
        Data=data,
        PartitionKey=f'sensor-{random.randint(1, 10)}'
    )
    i -= 1
