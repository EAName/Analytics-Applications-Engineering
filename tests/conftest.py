"""Shared fixtures.

ml_satellite creates a BigQuery client at import time, which needs GCP
credentials. Patch google.cloud.bigquery.Client before the module is imported
so the tests run offline, then hand each test a fresh mock client.
"""
import os
import sys
from unittest import mock

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

_client_patcher = mock.patch("google.cloud.bigquery.Client")
_client_patcher.start()

import ml_satellite  # noqa: E402  (must come after the patch)
import main as app_module  # noqa: E402


def make_query_job(rows):
    """Return a mock QueryJob whose result() yields the given rows.

    BigQuery Row objects support .keys() and item access, so plain dicts
    behave the same for the code under test.
    """
    job = mock.MagicMock()
    job.result.return_value = rows
    return job


@pytest.fixture
def bq_client(monkeypatch):
    client = mock.MagicMock(name="bigquery.Client()")
    monkeypatch.setattr(ml_satellite, "client", client)
    return client


@pytest.fixture
def flask_client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client
