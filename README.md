# Gmail Job Search Automation

![CI](https://github.com/atharvadevne123/Gmail-job-Automation/actions/workflows/ci.yml/badge.svg)

**By [Atharva Devne](https://github.com/atharvadevne123)**

A collection of scripts to automatically organize your job search emails in Gmail — labels rejections, applications, and interviews, and moves them out of your inbox. Built to handle 14,000+ emails with no manual work.

---

## Files Overview

| File | Type | Description |
|------|------|-------------|
| `gmail_labeler.py` | Python | **Main script** — labels rejections & applications. |
| `label_interviews.py` | Python | Labels interview invitation emails. |
| `delete_job_emails.py` | Python | Moves labeled emails to Trash. |
| `count_emails.py` | Python | Read-only thread counter (no changes). |
| `utils.py` | Python | Shared helpers used by all scripts. |
| `Makefile` | Config | Shortcuts: `make test`, `make lint`, etc. |
| `pyproject.toml` | Config | Build metadata, ruff, pytest, mypy settings. |

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

# 2. Get credentials.json from Google Cloud Console (Gmail API, OAuth Desktop)
# 3. Run a dry-run first
python gmail_labeler.py --dry-run

# 4. Apply labels
python gmail_labeler.py

# 5. Label interview emails
python label_interviews.py

# 6. Count what was labeled
python count_emails.py
```

---

## API Reference

### `auth.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_gmail_service` | `() -> Any` | Authenticate and return Gmail API service. |
| `with_retry` | `(fn, max_retries=5) -> Any` | Retry fn() with exponential backoff. |

### `gmail_labeler.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_or_create_label` | `(service, name, existing, dry_run) -> str` | Return label ID. |
| `label_threads` | `(service, label_name, label_id, queries, dry_run) -> int` | Label matching threads. |

### `label_interviews.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_or_create_label` | `(service, name) -> str` | Return label ID. |
| `label_interview_threads` | `(service, label_id, dry_run) -> int` | Label interview threads. |

### `delete_job_emails.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_label_id` | `(service, name) -> Optional[str]` | Look up label ID by name. |
| `trash_all_in_label` | `(service, label_name, label_id, dry_run) -> int` | Trash all threads in label. |

### `count_emails.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `count_label` | `(service, label_name) -> int` | Count threads in a label. |

### `utils.py`

| Function | Signature | Description |
|----------|-----------|-------------|
| `build_query` | `(terms, operator="OR") -> str` | Join search terms. |
| `chunked` | `(items, size) -> Generator` | Yield list chunks. |
| `format_count` | `(n, singular, plural=None) -> str` | Human-readable count. |

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Get credentials.json from Google Cloud**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. New Project → Enable **Gmail API**
3. Credentials → Create → **OAuth 2.0 Client ID** → Desktop app
4. Download JSON → rename to `credentials.json`
5. Place in same folder as the scripts

**3. (Optional) Override paths via environment variables**
```bash
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
export GMAIL_TOKEN_PATH=/path/to/token.pickle
```

---

## Running the Scripts

```bash
# Preview (no changes)
python gmail_labeler.py --dry-run

# Label rejections + applications
python gmail_labeler.py

# Label interview emails
python label_interviews.py

# Count threads (read-only)
python count_emails.py

# Permanently delete labeled emails
python delete_job_emails.py
```

---

## Testing

```bash
make test          # run pytest with coverage
make lint          # ruff check
make cover         # html coverage report
make type-check    # mypy
```

---

## License

MIT — free to use and modify.
