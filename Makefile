.PHONY: install test lint fix clean

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing

lint:
	python -m ruff check .

fix:
	python -m ruff check . --select E,F,W,I --ignore E501 --fix

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
