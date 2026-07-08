# Changelog

All notable changes to Gmail Job Automation are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `--dry-run` flag for `label_interviews.py` (parity with `gmail_labeler.py`)
- `--yes` flag for `delete_job_emails.py` enabling non-interactive / CI use
- `--log-level` flag for all three scripts (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- Google-style docstrings on all public functions and module docstrings
- `.pre-commit-config.yaml` with ruff and pre-commit-hooks
- `CONTRIBUTING.md` with setup, testing, and PR guidelines
- `[tool.ruff]` and `[tool.mypy]` configuration sections in `pyproject.toml`
- `scripts/run_all.py` — run all three labelers with a single authentication
- `utils.py` with `format_count()` and `plural_s()` helpers, used in all summaries
- Test suite expanded from 27 to 95 tests (parametrized retry codes, pagination,
  dry-run parity, main() flows, query-list integrity)
- `typing.Final` annotations on module constants
- Makefile: `help` (default), `test-fast`, `format`, `format-check`, `type-check`, `ci`,
  `run-all`, `run-all-dry` targets
- Repo hygiene: `.editorconfig`, `.gitattributes`, PR template, issue templates,
  `CODE_OF_CONDUCT.md`
- README rewritten with Features, Quick Start, CLI reference, and architecture diagram
- Merged upstream: `count_emails.py` (read-only counts with `--json`/`--csv`),
  `is_authenticated()` in `auth.py`, extra `utils` helpers (`build_query`, `chunked`,
  `format_duration`, `sanitize_query`, `truncate`, `retry`), `py.typed` marker,
  release workflow

### Fixed
- Unused imports in `scripts/run_all.py` and `tests/test_run_all.py`
- Loop-variable capture (ruff B023) in batch callbacks across all three scripts
- Pinned GitHub Actions to stable versions (`actions/checkout@v4`, `actions/setup-python@v5`)
- Type annotations added to `_cb` callbacks in `delete_job_emails.py`

## [1.0.0] - 2026-04-21

### Added
- Initial release with `gmail_labeler.py`, `label_interviews.py`, `delete_job_emails.py`
- OAuth2 authentication with token caching and auto-refresh (`auth.py`)
- Exponential-backoff retry logic for transient API errors (`with_retry`)
- `--dry-run` mode in `gmail_labeler.py`
- GitHub Actions CI workflow
- pytest test suite (27 tests)
- `pyproject.toml`, `Makefile`, `.env.example`, `SECURITY.md`
