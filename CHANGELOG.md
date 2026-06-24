# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `utils.py`: shared helpers (`build_query`, `chunked`, `format_count`,
  `sanitize_query`, `retry` decorator)
- `count_emails.py`: read-only thread counter with `--json` flag and `count_all`
- `py.typed` marker for PEP 561 compliance
- `__all__` exports on all public modules
- `NullHandler` on all module-level loggers
- `dry_run` parameter on `label_interview_threads` and `trash_all_in_label`
- `is_authenticated()` helper in `auth.py` to check token validity without I/O
- `batch_size` parameter on `label_threads` for tunable batch control
- Configurable entry points in `pyproject.toml` (`count-emails`, `label-jobs`,
  `label-interviews`, `delete-job-emails`)
- `.github/workflows/release.yml` for automated tag-triggered releases
- `cover`, `type-check`, `count`, `all` targets in `Makefile`
- mypy configuration in `pyproject.toml`
- Coverage artifact upload in CI

### Changed
- `label_interviews.py`: 24 query patterns (up from 19), added `dry_run` support
- `delete_job_emails.py`: shows per-label summary table and batch error counts
- `gmail_labeler.py`: `label_threads` accepts `batch_size` parameter
- `README.md`: rewrote with API Reference table and Quick Start section
- `pyproject.toml`: added `project.urls`, `scripts`, mypy, coverage config
- `Makefile`: added targets for full dev workflow
- CI workflow: added mypy step and coverage XML artifact

### Fixed
- Missing type annotations on `_cb` callback in `delete_job_emails.py`
- Import sort order in all modules (ruff I001)
- String quotes normalized to double quotes throughout

## [1.0.0] — Initial Release

### Added
- `gmail_labeler.py`: label job rejections and applications with `--dry-run`
- `label_interviews.py`: label interview invitation emails
- `delete_job_emails.py`: move labeled emails to Trash
- `auth.py`: Gmail OAuth2 with exponential backoff retry
- Full pytest test suite (27 tests) with mocked Google API
- CI workflow with ruff lint and pytest coverage gate
