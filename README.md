# Influx Data Sync

Influx Data Sync is a Python script designed to download JSON data from an HTTP endpoint and write it to InfluxDB.

## Configuration

Before running the script, ensure you have the following environment variables set:

    INFLUXDB_TOKEN: The token for authenticating with your InfluxDB instance.
    INFLUXDB_ORG: The InfluxDB organization.
    INFLUXDB_BUCKET: The target bucket in InfluxDB where data will be written.
    INFLUXDB_URL: The URL of your InfluxDB instance, including the port (e.g., http://localhost:8086).
    HTTP_ENDPOINT: The HTTP endpoint URL from which JSON data will be downloaded.
    MEASUREMENT_NAME: The name of the measurement that will be used in InfluxDB.
