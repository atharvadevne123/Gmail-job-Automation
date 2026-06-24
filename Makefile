.PHONY: install dev-install test cover lint fix type-check count clean all check release

all: lint test

install:
	pip install -r requirements.txt

dev-install:
	pip install -e ".[dev]"

check: lint type-check test

test:
	python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing

cover:
	python -m pytest tests/ --cov=. --cov-report=html --cov-fail-under=70
	@echo "Coverage report: htmlcov/index.html"

lint:
	python -m ruff check .

fix:
	python -m ruff check . --select E,F,W,I --ignore E501 --fix

type-check:
	python -m mypy . --ignore-missing-imports

count:
	python count_emails.py

release: lint test
	git tag -a v$$(python -c "import importlib.metadata; print(importlib.metadata.version('gmail-job-automation'))") -m "Release"
	@echo "Tag created. Push with: git push --tags"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ dist/ build/ *.egg-info/
