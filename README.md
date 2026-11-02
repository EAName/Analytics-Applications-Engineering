# Analytics-Applications-Engineering

Data Engineering specialization capstone: deployable analytics web service exposing BigQuery-backed satellite classification data and serving in-database ML predictions through a Flask API on Google Cloud Platform.

---

## 1. Title and Summary

**Analytics Applications Engineering (Data Engineering Specialization Capstone)**  
Northwestern University M.S. in Data Science, Data Engineering specialization: culminating specialization deliverable — a production-style client-server analytics application with REST endpoints, cloud data warehouse integration, BigQuery ML inference, automated testing/linting, and CI/CD deployment to Google App Engine.

---

## 2. Featured Project: Satellite Imagery Classification Application (SICA)

A Google Cloud application that automates classification of Landsat imagery, replacing manual labeling with on-demand predictions from a convolutional neural network.

**Architecture:** A Flask API on Google App Engine handles requests to retrieve SICA data and score new imagery against the ML model. BigQuery serves as the data warehouse, organized under the project `sat_model`, with the `dcp_ml` dataset housing the `sat_cnn` model used for training and testing classifications.

**Environments:** Separate development, staging, and production services on App Engine, each defined in its own YAML file with manual scaling policies that control CPU, memory, and disk allocation.

**Data pipeline:** A weekly ETL pipeline, scheduled with cron jobs, batch-updates the datasets.

**CI/CD:** Code is version-controlled on GitHub. CircleCI runs tests and linting on every push, then deploys to App Engine.

**Operations:** Google Cloud Monitoring tracks CPU usage, network bytes, and response counts, and supports log analysis for troubleshooting. Load testing with ApacheBench verified the application under varying workloads, and a cost model forecasts monthly spend so data scientists, data engineers, and DevOps engineers can tune resource usage.

**About this repository:** It contains the Flask service, BigQuery integration, App Engine service configs, and CircleCI pipeline. The staging configuration, scheduled ETL, CNN training, monitoring dashboards, load-test results, and cost model were built in the GCP project and are not included here.

---

## 3. Concepts and Methods

- **Web service design (Flask):** HTTP routes for health check (`/`), read-only analytics export (`GET /get-model`), and CSV upload with prediction response (`POST /satellite-model`); JSON responses via `app.response_class`
- **Cloud data warehouse integration (BigQuery):** `google-cloud-bigquery` client; query existing `sat_analytics` table; load uploaded CSV into ephemeral tables with autodetect schema, `WRITE_TRUNCATE`, and timestamped table names
- **In-database ML inference:** `ML.PREDICT` against pre-trained BigQuery model `sample_model` over uploaded feature columns (`Aattr` through `F30attr`, `class` as label); return prediction rows as JSON
- **Packaging and local execution:** `gunicorn` entrypoint for App Engine Flex; `run.sh` for local dev with `GOOGLE_APPLICATION_CREDENTIALS`
- **Software engineering workflow:** `Makefile` targets for `venv`, `install`, `pytest` with coverage, and `pylint`; reusable `myrepolib` module pattern for importable library code and unit tests
- **CI/CD (CircleCI):** dependency cache, `make test`, `make lint`, authenticated `gcloud app deploy` on merge
- **Multi-service deployment:** separate App Engine service configs for `default`, `dev`, and `production` (`app.yaml`, `servicedev.yaml`, `serviceprod.yaml`); `deploy.sh` deploys all three

**Project domain:** satellite analytics classification use case; `model.json` holds sample feature records aligned with model input schema

---

## 4. Stack

| Layer | Tools |
|-------|-------|
| Language | Python 3 |
| Web framework | Flask, gunicorn |
| Cloud platform | Google Cloud Platform (App Engine Flex, BigQuery, BigQuery ML) |
| Data / ML | `google-cloud-bigquery`, BigQuery `ML.PREDICT` |
| Testing / quality | pytest, pytest-cov, pylint, nbval |
| CI/CD | CircleCI (`google/cloud-sdk` image), `gcloud app deploy` |
| Config / ops | YAML (`app.yaml`, service variants), Shell (`deploy.sh`, `run.sh`), Makefile |
| Library pattern | `myrepolib` (importable package + tests) |

---

## 5. Structure

```
Analytics-Applications-Engineering/
├── main.py                 # Flask app and route definitions
├── ml_satellite.py         # BigQuery query, CSV load, ML.PREDICT logic
├── myrepolib/
│   └── main.py             # Reusable library stubs (requests helper, test hooks)
├── tests/
│   └── test_main.py        # Unit tests for myrepolib
├── app.yaml                # App Engine default service
├── servicedev.yaml         # App Engine dev service
├── serviceprod.yaml        # App Engine production service
├── deploy.sh               # Multi-service deploy script
├── run.sh                  # Local run with credentials
├── Makefile                # install, test, lint targets
├── requirements.txt
├── model.json              # Sample feature records for model input schema
├── .circleci/config.yml    # CI test, lint, deploy pipeline
└── README.md
```

- **Organization:** thin Flask layer over BigQuery/ML module; library + test scaffold separated in `myrepolib/`
- **Reusable modules:** `ml_satellite.query_data()`, `ml_satellite.load_csv()`; `myrepolib.main.myfunc()` and HTTP helper stubs
- **Engineering practice:** cloud-hosted analytics API, ephemeral upload tables, JSON serialization of warehouse rows, multi-environment YAML configs, automated deploy after test/lint gate

---

**Course context:** Northwestern University, M.S. in Data Science, Data Engineering specialization (Data Engineering specialization capstone)  
**Repository:** https://github.com/EAName/Analytics-Applications-Engineering
