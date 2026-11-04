"""Tests for the Flask routes and BigQuery calls, with BigQuery mocked out."""
import io
import json
from unittest import mock

import pytest

import main
import ml_satellite


class FakeRow(dict):
    """Stands in for google.cloud.bigquery.Row (supports keys() and [key])."""


def query_job(rows):
    job = mock.Mock()
    job.result.return_value = rows
    return job


@pytest.fixture(name="client")
def fixture_client():
    fake_bq = mock.Mock()
    with mock.patch.object(ml_satellite, "_client", fake_bq):
        yield fake_bq


@pytest.fixture(name="app_client")
def fixture_app_client():
    main.app.config["TESTING"] = True
    return main.app.test_client()


def test_import_needs_no_credentials():
    # The BigQuery client is created lazily, so importing the app never
    # touches GCP. This is what lets the tests and pylint run in CI.
    assert ml_satellite.get_client is not None
    assert main.app.name == "main"


def test_hello(app_client):
    res = app_client.get("/")
    assert res.status_code == 200
    assert res.data == b"Hello World!"


def test_get_model(app_client, client):
    client.query.return_value = query_job(
        [FakeRow(A=1.29, label=2), FakeRow(A=-0.35, label=1)]
    )
    res = app_client.get("/get-model")
    assert res.status_code == 200
    assert res.mimetype == "application/json"
    assert json.loads(res.data) == [{"A": "1.29", "label": "2"}, {"A": "-0.35", "label": "1"}]
    sql = client.query.call_args.args[0]
    assert "`flight-data-1.dsongcp.sat_analytics`" in sql
    assert "LIMIT 1000" in sql


def test_satellite_model_predicts_and_cleans_up(app_client, client):
    client.query.return_value = query_job(
        [FakeRow(predicted_label=2, label=2, A=-1.878905)]
    )
    uploaded = {}

    def fake_load(file_obj, table_id, job_config):
        # Read here: Flask closes the upload stream once the request ends.
        assert job_config.skip_leading_rows == 1
        uploaded.update(data=file_obj.read(), table_id=table_id)
        return mock.Mock()

    client.load_table_from_file.side_effect = fake_load
    csv = b"Aattr,Battr,class\n-1.878905,-2.167396,2\n"
    res = app_client.post(
        "/satellite-model",
        data={"file": (io.BytesIO(csv), "upload.csv")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200
    assert json.loads(res.data) == [{"predicted_label": "2", "label": "2", "A": "-1.878905"}]

    # The upload is loaded into a fresh table and that table is scored.
    table_id = uploaded["table_id"]
    assert uploaded["data"] == csv
    assert table_id.startswith("flight-data-1.dsongcp.sat_upload_")
    sql = client.query.call_args.args[0]
    assert "ML.PREDICT(MODEL `flight-data-1.dsongcp.sample_model`" in sql
    assert f"FROM `{table_id}`" in sql
    # Only the prediction query runs (no throwaway SELECT *).
    assert client.query.call_count == 1
    client.delete_table.assert_called_once_with(table_id, not_found_ok=True)


def test_satellite_model_deletes_table_when_query_fails(client):
    client.query.side_effect = RuntimeError("model not found")
    with pytest.raises(RuntimeError):
        ml_satellite.load_csv(io.BytesIO(b"Aattr\n1\n"))
    client.delete_table.assert_called_once()


def test_upload_tables_are_unique(client):
    client.query.return_value = query_job([])
    ml_satellite.load_csv(io.BytesIO(b"x\n1\n"))
    ml_satellite.load_csv(io.BytesIO(b"x\n1\n"))
    first, second = [c.args[1] for c in client.load_table_from_file.call_args_list]
    assert first != second


def test_satellite_model_without_file(app_client, client):
    res = app_client.post("/satellite-model", data={}, content_type="multipart/form-data")
    assert res.status_code == 400
    assert "error" in json.loads(res.data)
    client.load_table_from_file.assert_not_called()


def test_predict_query_maps_all_36_features():
    sql = ml_satellite.build_predict_query("p.d.t")
    assert "class AS label" in sql
    for name in ml_satellite.FEATURES:
        assert f"{name}attr AS {name}," in sql or f"{name}attr AS {name}\n" in sql
    assert len(ml_satellite.FEATURES) == 36
    # The model schema in model.json uses the same 36 feature names plus label.
    with open("model.json", encoding="utf-8") as handle:
        sample = json.load(handle)[0]
    assert set(sample) == set(ml_satellite.FEATURES) | {"label"}
