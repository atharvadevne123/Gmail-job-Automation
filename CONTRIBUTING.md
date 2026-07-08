# Contributing

Thank you for your interest in contributing to Gmail Job Automation!

## Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements-dev.txt`
4. Install pre-commit hooks: `pre-commit install`

## Making Changes

- Keep each pull request focused on a single concern.
- Run `make lint` before committing — the CI will fail on ruff errors.
- Run `make test` to verify all tests pass before opening a PR.
- Follow the existing code style (Google-style docstrings, type annotations on all public functions).

## Running Tests

```bash
make test
# or
python -m pytest tests/ -v --tb=short
```

## Submitting a Pull Request

1. Push your branch to your fork.
2. Open a pull request against `main` in this repository.
3. Describe what the PR does and why.
4. A maintainer will review and merge it.

## Reporting Issues

Use [GitHub Issues](../../issues) to report bugs or request features.
Please include steps to reproduce and the expected vs. actual behaviour.
