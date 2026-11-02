"""Unit tests for ml_satellite with the BigQuery client mocked out."""
import io
from datetime import datetime
from unittest import mock

from google.cloud import bigquery

import ml_satellite
from conftest import make_query_job


def test_query_data_reads_sat_analytics_table(bq_client):
    bq_client.query.return_value = make_query_job([])

    ml_satellite.query_data()

    sql = bq_client.query.call_args.args[0]
    assert "`flight-data-1.dsongcp.sat_analytics`" in sql
    assert "LIMIT 1000" in sql


def test_query_data_serializes_every_value_as_string(bq_client):
    rows = [
        {"A": 1.293559, "label": 3, "note": None},
        {"A": 0.5, "label": 1, "note": "x"},
    ]
    bq_client.query.return_value = make_query_job(rows)

    result = ml_satellite.query_data()

    assert result == [
        {"A": "1.293559", "label": "3", "note": "None"},
        {"A": "0.5", "label": "1", "note": "x"},
    ]


def test_query_data_empty_result(bq_client):
    bq_client.query.return_value = make_query_job([])
    assert ml_satellite.query_data() == []


def test_load_csv_loads_into_timestamped_table_with_truncate(bq_client, monkeypatch):
    fixed_now = datetime(2022, 8, 1, 12, 0, 0)
    fake_datetime = mock.MagicMock(wraps=datetime)
    fake_datetime.now.return_value = fixed_now
    monkeypatch.setattr(ml_satellite, "datetime", fake_datetime)

    bq_client.query.return_value = make_query_job([])
    upload = io.BytesIO(b"class,Aattr\n3,1.0\n")

    ml_satellite.load_csv(upload)

    expected_table = f"flight-data-1.dsongcp.sat_upload_{round(datetime.timestamp(fixed_now))}"
    args, kwargs = bq_client.load_table_from_file.call_args
    assert args[0] is upload
    assert args[1] == expected_table

    job_config = kwargs["job_config"]
    assert job_config.source_format == bigquery.SourceFormat.CSV
    assert job_config.skip_leading_rows == 1
    assert job_config.autodetect is True
    assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_TRUNCATE

    # load job is awaited before querying
    bq_client.load_table_from_file.return_value.result.assert_called_once()


def test_load_csv_runs_ml_predict_against_uploaded_table(bq_client):
    bq_client.query.return_value = make_query_job([])

    ml_satellite.load_csv(io.BytesIO(b"class,Aattr\n3,1.0\n"))

    table_id = bq_client.load_table_from_file.call_args.args[1]
    ml_sql = bq_client.query.call_args_list[-1].args[0]
    assert "ML.PREDICT(MODEL `flight-data-1.dsongcp.sample_model`" in ml_sql
    assert f"FROM `{table_id}`" in ml_sql
    # feature renames: raw upload columns (Aattr ... F30attr) map to model inputs
    assert "class AS label" in ml_sql
    assert "Aattr AS A," in ml_sql
    assert "F30attr AS F30" in ml_sql


def test_load_csv_returns_prediction_rows_as_strings(bq_client):
    preview_job = make_query_job([{"ignored": 1}])
    predict_job = make_query_job([
        {"predicted_label": 3, "label": 3, "A": 1.29},
        {"predicted_label": 1, "label": 2, "A": 0.4},
    ])
    bq_client.query.side_effect = [preview_job, predict_job]

    result = ml_satellite.load_csv(io.BytesIO(b"class,Aattr\n3,1.29\n2,0.4\n"))

    assert result == [
        {"predicted_label": "3", "label": "3", "A": "1.29"},
        {"predicted_label": "1", "label": "2", "A": "0.4"},
    ]
    # Current behavior: a preview SELECT runs before ML.PREDICT and its result is unused.
    assert bq_client.query.call_count == 2
