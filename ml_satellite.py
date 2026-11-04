import os
import uuid

from google.cloud import bigquery

# BigQuery location of the analytics table and the BQML model. Override with
# environment variables instead of editing code when the GCP project changes.
PROJECT = os.environ.get("BQ_PROJECT", "flight-data-1")
DATASET = os.environ.get("BQ_DATASET", "dsongcp")
MODEL = os.environ.get("BQ_MODEL", "sample_model")

FEATURES = [
    "A", "B", "C", "D", "E", "F",
    "A1", "B2", "C3", "D4", "E5", "F6",
    "A7", "B8", "C9", "D10", "E11", "F12",
    "A13", "B14", "C15", "D16", "E17", "F18",
    "A19", "B20", "C21", "D22", "E23", "F24",
    "A25", "B26", "C27", "D28", "E29", "F30",
]

_client = None


def get_client():
    """Create the BigQuery client on first use, so importing the app does not
    require GCP credentials (tests, linting, local startup)."""
    global _client  # pylint: disable=global-statement
    if _client is None:
        _client = bigquery.Client(project=PROJECT)
    return _client


def rows_to_json(rows):
    """Convert BigQuery rows to a list of dicts with string values."""
    results_json = []
    for row in rows:
        row_json = {}
        for key in row.keys():
            row_json[key] = str(row[key])
        results_json.append(row_json)
    return results_json


def query_data():
    query = f"SELECT * FROM `{PROJECT}.{DATASET}.sat_analytics` LIMIT 1000"
    results = get_client().query(query).result()
    return rows_to_json(results)


def build_predict_query(table_id):
    """ML.PREDICT query that maps the uploaded CSV columns (Aattr, Battr, ...,
    class) to the feature names the model was trained on."""
    columns = ",\n    ".join(f"{name}attr AS {name}" for name in FEATURES)
    return f"""
SELECT * FROM ML.PREDICT(MODEL `{PROJECT}.{DATASET}.{MODEL}`,
  (
  SELECT class AS label,
    {columns}
  FROM `{table_id}`))
"""


def load_csv(csv):
    client = get_client()
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    # A random suffix keeps two uploads in the same second from overwriting
    # each other's table (the old name used a whole-second timestamp).
    table_id = f"{PROJECT}.{DATASET}.sat_upload_{uuid.uuid4().hex}"

    try:
        job = client.load_table_from_file(csv, table_id, job_config=job_config)
        job.result()
        ml_result = client.query(build_predict_query(table_id)).result()
        return rows_to_json(ml_result)
    finally:
        # The upload table is only needed for this one prediction.
        client.delete_table(table_id, not_found_ok=True)
