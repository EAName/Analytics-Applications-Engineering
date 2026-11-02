# Local run. Point GOOGLE_APPLICATION_CREDENTIALS at a service account key with
# BigQuery access; defaults to ./secrets/creds.json (git-ignored).
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-./secrets/creds.json}"
python main.py
