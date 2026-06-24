# Gmail Job Search Automation

![CI](https://github.com/atharvadevne123/Gmail-job-Automation/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**By [Atharva Devne](https://github.com/atharvadevne123)**

A collection of scripts to automatically organize your job search emails in Gmail — labels rejections, applications, and interviews, and moves them out of your inbox. Built to handle 14,000+ emails with no manual work.

---

## Architecture

```
Gmail API (OAuth2)
       │
   auth.py  ──── token.pickle (cached credentials)
       │
       ├── gmail_labeler.py    ─── labels rejections & applications
       ├── label_interviews.py ─── labels interview invitations
       ├── delete_job_emails.py ── moves labeled emails to Trash
       └── count_emails.py     ─── read-only thread counts
               │
           utils.py  ─── shared helpers (build_query, chunked, format_count)
```

---

## Files Overview

| File | Type | Description |
|------|------|-------------|
| `gmail_labeler.py` | Python | **Main script** — labels rejections & applications. |
| `label_interviews.py` | Python | Labels interview invitation emails. |
| `delete_job_emails.py` | Python | Moves labeled emails to Trash. |
| `count_emails.py` | Python | Read-only thread counter (no changes). |
| `utils.py` | Python | Shared helpers used by all scripts. |
| `auth.py` | Python | Gmail OAuth2 + exponential-backoff retry. |

---

## Labels Created

- **Job Rejections** — emails where you were not selected
- **Job Applications Applied** — confirmation emails when you applied
- **Job Interviews** — emails inviting you to interview

---

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Get credentials.json from Google Cloud Console:
#    New Project → Enable Gmail API → OAuth Desktop → Download → rename credentials.json

# 3. Dry-run to preview (no changes made)
python gmail_labeler.py --dry-run

# 4. Apply labels
python gmail_labeler.py

# 5. Label interview emails
python label_interviews.py

# 6. Count labeled threads
python count_emails.py
python count_emails.py --json
python count_emails.py --csv
```

---

## API Reference

### `auth.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_gmail_service` | `() -> Any` | Authenticate and return Gmail API service. |
| `with_retry` | `(fn, max_retries=5) -> Any` | Retry with exponential backoff. |
| `is_authenticated` | `() -> bool` | Check if valid token exists. |

### `gmail_labeler.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_or_create_label` | `(service, name, existing, dry_run) -> str` | Return label ID. |
| `label_threads` | `(service, name, id, queries, dry_run, batch_size) -> int` | Label threads. |

### `label_interviews.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_or_create_label` | `(service, name) -> str` | Return label ID. |
| `label_interview_threads` | `(service, label_id, dry_run) -> int` | Label interview threads. |

### `delete_job_emails.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_label_id` | `(service, name) -> Optional[str]` | Look up label ID. |
| `trash_all_in_label` | `(service, name, id, dry_run) -> int` | Trash all threads. |

### `count_emails.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `count_label` | `(service, label_name) -> int` | Count threads in a label. |
| `count_all` | `(service, labels) -> dict` | Count multiple labels. |
| `export_csv` | `(counts, output) -> None` | Write counts as CSV. |

### `utils.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `build_query` | `(terms, operator) -> str` | Join search terms. |
| `chunked` | `(items, size) -> Generator` | Yield list chunks. |
| `format_count` | `(n, singular, plural) -> str` | Human-readable count. |
| `format_duration` | `(seconds) -> str` | Human-readable duration. |
| `sanitize_query` | `(query) -> str` | Normalize whitespace in query. |
| `retry` | `(max_retries, delay, exceptions) -> Callable` | Retry decorator. |

---

## Testing

```bash
make test           # pytest with coverage
make cover          # HTML coverage report (htmlcov/index.html)
make lint           # ruff check
make type-check     # mypy
make check          # lint + type-check + test
```

---

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Get `credentials.json` from [Google Cloud Console](https://console.cloud.google.com) (Gmail API, OAuth Desktop app)
3. Optionally set `GMAIL_CREDENTIALS_PATH` and `GMAIL_TOKEN_PATH` env vars

---

## License

MIT — free to use and modify.
