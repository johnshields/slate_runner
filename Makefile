VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(PYTHON) -m pip

venv:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel

install: venv
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn src.main:app --host 127.0.0.1 --port 8049 --reload

clean:
	rm -rf $(VENV) __pycache__ */__pycache__

freeze:
	$(PIP) freeze > requirements.txt
