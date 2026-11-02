"""Flask route tests for main.py; ml_satellite is stubbed so no GCP access is needed."""
import io
import json

import ml_satellite


def test_health_route(flask_client):
    resp = flask_client.get("/")
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == "Hello World!"


def test_get_model_returns_query_rows_as_json(flask_client, monkeypatch):
    rows = [{"A": "1.29", "label": "3"}, {"A": "0.4", "label": "2"}]
    monkeypatch.setattr(ml_satellite, "query_data", lambda: rows)

    resp = flask_client.get("/get-model")

    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    assert json.loads(resp.data) == rows


def test_satellite_model_passes_upload_to_load_csv(flask_client, monkeypatch):
    received = {}

    def fake_load_csv(upload):
        received["filename"] = upload.filename
        received["content"] = upload.read()
        return [{"predicted_label": "3", "label": "3"}]

    monkeypatch.setattr(ml_satellite, "load_csv", fake_load_csv)
    csv_bytes = b"class,Aattr,Battr\n3,1.293559,0.848043\n"

    resp = flask_client.post(
        "/satellite-model",
        data={"file": (io.BytesIO(csv_bytes), "sample.csv")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    assert json.loads(resp.data) == [{"predicted_label": "3", "label": "3"}]
    assert received == {"filename": "sample.csv", "content": csv_bytes}


def test_satellite_model_without_file_is_bad_request(flask_client, monkeypatch):
    called = []
    monkeypatch.setattr(ml_satellite, "load_csv", lambda f: called.append(f))

    resp = flask_client.post("/satellite-model", data={}, content_type="multipart/form-data")

    assert resp.status_code == 400
    assert called == []


def test_satellite_model_rejects_get(flask_client):
    assert flask_client.get("/satellite-model").status_code == 405
