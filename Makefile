.DEFAULT_GOAL := help
.PHONY: help install install-dev test test-fast lint fix format format-check type-check ci clean count cover run-all run-all-dry

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install runtime dependencies
	pip install -r requirements.txt

install-dev:  ## Install runtime + dev/test dependencies
	pip install -r requirements-dev.txt

test:  ## Run the full test suite with coverage
	python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing

test-fast:  ## Run tests, stop on first failure
	python -m pytest tests/ -x --tb=short -q

lint:  ## Check code style with ruff
	python -m ruff check .

fix:  ## Auto-fix lint issues
	python -m ruff check . --select E,F,W,I --ignore E501 --fix

format:  ## Format code with ruff format
	python -m ruff format .

format-check:  ## Check formatting without modifying files
	python -m ruff format --check .

type-check:  ## Run mypy static analysis
	python -m mypy auth.py gmail_labeler.py label_interviews.py delete_job_emails.py utils.py --ignore-missing-imports

ci: lint test  ## Run everything CI runs (lint + tests)

count:  ## Count threads in job labels (read-only)
	python count_emails.py

cover:  ## HTML coverage report (htmlcov/index.html)
	python -m pytest tests/ --cov=. --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

run-all:  ## Run all three labelers with one auth
	python scripts/run_all.py

run-all-dry:  ## Preview all labelers without changes
	python scripts/run_all.py --dry-run

clean:  ## Remove caches and coverage artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
