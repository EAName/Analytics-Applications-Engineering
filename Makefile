setup:
	python -m venv ./venv

install:
	pip install -r requirements.txt

test:
	python -m pytest -vv --cov=myrepolib --cov=main --cov=ml_satellite tests/

lint:
	pylint --disable=R,C myrepolib main.py ml_satellite.py

lint2:
	PYTHONPATH=. pylint --disable=R,C tests

all: install lint lint2 test