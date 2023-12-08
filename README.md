# VM Data Sync

VM Data Sync is a Python script designed to download JSON data from an HTTP endpoint and write it to VictoriaMetrics.

## Configuration

Before running the script, ensure you have the following environment variables set:

    VICTORIAMETRICS_URL: The URL of your VictoriaMetrics instance, including the port and the write path (e.g., http://localhost:8428/write).
    MEASUREMENT_NAME: The name of the measurement that will be used in VictoriaMetrics. This is also the value of the *job* label.
    INSTANCE_NAME: The value of the *instance* label.
    HTTP_ENDPOINT: The HTTP endpoint URL from which JSON data will be downloaded.
