import logging
import os
import time

import requests
import schedule

# Logging module configuration
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

# VictoriaMetrics configuration
victoriametrics_url = os.getenv("VICTORIAMETRICS_URL", "http://localhost:8428/write")
measurement_name = os.getenv("MEASUREMENT_NAME", "default_measurement")
instance_name = os.getenv("INSTANCE_NAME", "127.0.0.1:80")

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


# Function to write data to VictoriaMetrics
def write_to_victoriametrics(data):
    if data.get("Cnt", 0) == 0:
        logging.info("'Cnt' value is zero. No write operation performed.")
        return

    # This is not a metric
    del data["Mac"]

    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        payload = f"{measurement_name},instance={instance_name},job={measurement_name} {','.join([f'{key.lower()}={value}' for key, value in data.items()])}\n"

        response = requests.post(
            victoriametrics_url,
            headers=headers,
            data=payload,
        )

        response.raise_for_status()

        logging.info("Data successfully written to VictoriaMetrics.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error writing data to VictoriaMetrics: {e}")


# Function to sync data
def job():
    logging.info("Downloading JSON with data...")
    json_data = download_json()

    if json_data:
        write_to_victoriametrics(json_data)
    else:
        logging.error("Error in downloading JSON or no data available.")


# Schedule the job function to run
schedule.every(1).minutes.do(job)

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
