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
- `[tool.ruff]` configuration section in `pyproject.toml`

### Fixed
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
