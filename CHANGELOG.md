# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- `utils.py`: shared helpers (`build_query`, `chunked`, `format_count`)
- `count_emails.py`: read-only thread counter for job labels
- `py.typed` marker for PEP 561 compliance
- `__all__` exports on all public modules
- `NullHandler` on all module-level loggers to silence "No handler" warnings
- `dry_run` parameter on `label_interviews.label_interview_threads`
- Type annotations on `delete_job_emails._cb` callback
- `.github/workflows/release.yml` for automated PyPI-style releases

### Changed
- `auth.py`: added module docstring and `__all__`
- `gmail_labeler.py`: extracted `_build_search_query` helper
- `label_interviews.py`: accepts `dry_run` flag
- `delete_job_emails.py`: fixed missing type annotations on inner function

### Fixed
- Import sort order in all modules (ruff I001)
