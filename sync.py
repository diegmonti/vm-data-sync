import logging
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

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

# Variable to keep track of the timestamp of the last successful job
last_successful_job_timestamp = time.time()


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

        # Update the timestamp of the last successful job
        global last_successful_job_timestamp
        last_successful_job_timestamp = time.time()

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


# HTTP handler for health check
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global last_successful_job_timestamp

        current_time = time.time()

        if current_time - last_successful_job_timestamp <= 300:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("OK", "utf8"))
        else:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(
                bytes("Error: Last successful job is more than 5 minutes old", "utf8")
            )


# Set up the HTTP server
port = 8080
http_server = HTTPServer(("localhost", port), HealthHandler)

logging.info(f"Health check server started on port {port}")

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
    http_server.handle_request()
