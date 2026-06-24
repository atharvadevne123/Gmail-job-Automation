# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `utils.py`: `build_query`, `chunked`, `format_count`, `format_duration`,
  `sanitize_query`, `retry` decorator
- `count_emails.py`: `count_all`, `export_csv`, `--json`/`--csv` CLI flags
- `py.typed` marker for PEP 561 compliance
- `__all__` exports on all public modules
- `NullHandler` on all module-level loggers
- `is_authenticated()` in `auth.py`
- `batch_size` param on `label_threads` in `gmail_labeler.py`
- `REJECTION_LABEL` / `APPLICATION_LABEL` constants in `gmail_labeler.py`
- `LABEL_COLOR` constant in `label_interviews.py`
- `dry_run` param on `label_interview_threads` and `trash_all_in_label`
- `--labels` CLI flag on `delete_job_emails.py` for custom targets
- `[project.optional-dependencies] dev` group in `pyproject.toml`
- `dev-install`, `check` targets in `Makefile`
- Python 3.12 in CI test matrix
- Release workflow for version tags
- Coverage XML artifact upload in CI

### Changed
- `label_interviews.py`: 24 query patterns (up from 19)
- `delete_job_emails.py`: per-label summary table
- `README.md`: architecture diagram, badges, API reference tables
- `pyproject.toml`: `project.urls`, `scripts`, mypy, ruff per-file-ignores

### Fixed
- Missing type annotations on `_cb` callback (delete_job_emails, label_interviews)
- Import sort order in all modules

## [1.0.0] — 2024-01-01

### Added
- `gmail_labeler.py`: label job rejections and applications with `--dry-run`
- `label_interviews.py`: label interview invitation emails
- `delete_job_emails.py`: move labeled emails to Trash
- `auth.py`: Gmail OAuth2 with exponential backoff retry
- Full pytest test suite (27 tests) with mocked Google API
- CI workflow with ruff lint and pytest coverage gate
