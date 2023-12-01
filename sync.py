import logging
import os
import time
from datetime import datetime

import requests
import schedule
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision

# Logging module configuration
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# InfluxDB configuration
influxdb_token = os.getenv("INFLUXDB_TOKEN", "default_token")
influxdb_org = os.getenv("INFLUXDB_ORG", "default_org")
influxdb_bucket = os.getenv("INFLUXDB_BUCKET", "default_bucket")
influxdb_url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
measurement_name = os.getenv("MEASUREMENT_NAME", "default_measurement")

# HTTP endpoint configuration
http_endpoint = os.getenv("HTTP_ENDPOINT", "http://localhost/status")


# Function to download JSON from the HTTP endpoint
def download_json():
    try:
        response = requests.get(http_endpoint)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error downloading JSON: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Connection error: {e}")
        return None


# Function to write data to InfluxDB
def write_to_influxdb(data):
    client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    current_time = datetime.utcnow()

    if data.get("Cnt", 0) == 0:
        logging.info("'Cnt' value is zero. No write operation performed.")
        client.close()
        return

    point = Point(measurement_name).time(current_time, WritePrecision.NS)

    for key, value in data.items():
        field_name = key.replace(" ", "_").lower()
        if isinstance(value, str):
            point.field(field_name, value)
        else:
            point.field(field_name, float(value))

    write_api.write(bucket=influxdb_bucket, record=point)

    client.close()


# Function to sync data
def job():
    logging.info("Downloading JSON with data...")
    json_data = download_json()

    if json_data:
        write_to_influxdb(json_data)
        logging.info("Data successfully written to InfluxDB.")
    else:
        logging.error("Error in downloading JSON or no data available.")


# Schedule the job function to run
schedule.every(5).minutes.do(job)

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
