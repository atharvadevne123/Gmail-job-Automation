.PHONY: install test lint fix clean run-all run-all-dry type-check

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing

test-fast:
	python -m pytest tests/ -x --tb=short -q

lint:
	python -m ruff check .

fix:
	python -m ruff check . --select E,F,W,I --ignore E501 --fix

type-check:
	python -m mypy auth.py gmail_labeler.py label_interviews.py delete_job_emails.py utils.py --ignore-missing-imports

run-all:
	python scripts/run_all.py

run-all-dry:
	python scripts/run_all.py --dry-run

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
