# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project structure

```
.
├── auth.py               # Gmail OAuth2 + retry utilities
├── gmail_labeler.py      # Main labeling script
├── label_interviews.py   # Interview labeling
├── delete_job_emails.py  # Trash mover
├── count_emails.py       # Read-only counter
├── utils.py              # Shared helpers
├── tests/
│   ├── conftest.py       # Shared fixtures (mocks Google API)
│   └── test_*.py         # Test modules
└── Makefile              # Dev shortcuts
```

## Running tests

```bash
make test           # pytest with coverage
make cover          # HTML coverage report
```

Tests mock all Google API calls — no credentials needed.

## Code style

```bash
make lint           # ruff check
make fix            # ruff --fix
make type-check     # mypy
```

## Commit conventions

Use conventional commit prefixes:
- `feat:` new feature
- `fix:` bug fix
- `refactor:` code restructure
- `test:` test additions
- `docs:` documentation
- `chore:` tooling / config

## Adding a new label category

1. Add the label name constant and query list to the appropriate module
2. Add the label to `LABELS_TO_COUNT` in `count_emails.py` if countable
3. Write tests in `tests/` mocking the new label
4. Update `README.md` with the new label name

## Submitting changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Run `make lint test` before pushing
4. Open a pull request against `main`
