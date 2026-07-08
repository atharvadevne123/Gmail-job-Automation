# Gmail Job Search Automation

![CI](https://github.com/atharvadevne123/Gmail-job-Automation/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**By [Atharva Devne](https://github.com/atharvadevne123)**

A Python toolkit that automatically organises your job-search emails in Gmail — labelling rejections, application confirmations, and interview invitations, then archiving them out of your inbox. Built to handle 14,000+ emails with no time limits.

---

## Features

- **Label rejections** — detects 34 rejection phrases and applies "Job Rejections"
- **Label applications** — detects 25 confirmation phrases and applies "Job Applications Applied"
- **Label interviews** — detects 19 invitation patterns and applies "Job Interviews"
- **`--dry-run` mode** — preview match counts without modifying anything (all three scripts)
- **`--log-level`** — control verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- **`scripts/run_all.py`** — authenticate once and run all three labelers in sequence
- **Exponential backoff** — automatic retry on transient API errors (429, 500, 503)
- **Batch API** — 100 threads per HTTP request for maximum throughput

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
# or
make install
```

### 2. Get credentials from Google Cloud

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. New Project → Enable **Gmail API**
3. Credentials → Create → **OAuth 2.0 Client ID** → Desktop app
4. Download JSON → rename to `credentials.json`, place alongside the scripts
5. APIs & Services → OAuth consent screen → Test users → add your Gmail address

### 3. (Optional) Override paths via environment variables

```bash
cp .env.example .env
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
export GMAIL_TOKEN_PATH=/path/to/token.pickle
```

---

## Usage

### Preview without making changes

```bash
python gmail_labeler.py --dry-run
python label_interviews.py --dry-run
python scripts/run_all.py --dry-run
```

### Run individual labelers

```bash
python gmail_labeler.py          # labels rejections + applications
python label_interviews.py       # labels interview invitations
python delete_job_emails.py      # moves labeled emails to Trash
```

### Run all labelers in one pass

```bash
python scripts/run_all.py
# or
make run-all
make run-all-dry
```

### Keep your Mac awake during a long run

```bash
caffeinate -i python gmail_labeler.py
```

---

## CLI Reference

### `gmail_labeler.py`

| Flag | Default | Description |
|------|---------|-------------|
| `--dry-run` | off | Preview counts without modifying any emails |
| `--log-level` | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### `label_interviews.py`

| Flag | Default | Description |
|------|---------|-------------|
| `--dry-run` | off | Preview counts without modifying any emails |
| `--log-level` | `INFO` | Logging verbosity |

### `delete_job_emails.py`

| Flag | Default | Description |
|------|---------|-------------|
| `--yes` | off | Skip interactive confirmation (for CI / scripts) |
| `--log-level` | `INFO` | Logging verbosity |

### `scripts/run_all.py`

| Flag | Default | Description |
|------|---------|-------------|
| `--dry-run` | off | Pass dry-run to all labelers |
| `--log-level` | `INFO` | Logging verbosity |

---

## Labels Created

| Label | What it catches |
|-------|----------------|
| **Job Rejections** | "not be moving forward", "regret to inform", "the role has been filled", and 31 more phrases |
| **Job Applications Applied** | "thank you for applying", "application received", "we will review your application", and 22 more phrases |
| **Job Interviews** | "invitation to interview", "phone screen", "technical interview", and 16 more phrases |

---

## Architecture

```
Gmail API
    │
    ├── auth.py              OAuth2 flow + token caching + with_retry()
    │
    ├── gmail_labeler.py     Rejections + Applications (--dry-run support)
    ├── label_interviews.py  Interview invitations   (--dry-run support)
    ├── delete_job_emails.py Trash labeled emails    (--yes for CI)
    │
    └── scripts/run_all.py   Orchestrates all three with one auth call
```

---

## Testing

The test suite mocks all Gmail API calls — no credentials required.

```bash
make test         # pytest with coverage
make test-fast    # stop on first failure
make type-check   # mypy static analysis
```

**Test coverage (84+ tests):**

| Test file | Coverage |
|-----------|----------|
| `tests/test_auth.py` | `with_retry()` backoff, all retryable/non-retryable codes, token refresh |
| `tests/test_labeler.py` | label CRUD, pagination, dry-run, large batches, parametrized |
| `tests/test_delete.py` | label lookup, trash + pagination, main() flows |
| `tests/test_label_interviews.py` | dry-run parity, pagination, parametrized |
| `tests/test_main_flows.py` | end-to-end main() smoke tests |
| `tests/test_run_all.py` | orchestration, label completeness |
| `tests/test_utils.py` | format_count(), plural_s() |

**Makefile shortcuts:**

```bash
make install       # pip install -r requirements.txt
make test          # pytest with coverage report
make lint          # ruff check
make fix           # ruff --fix
make run-all       # python scripts/run_all.py
make run-all-dry   # python scripts/run_all.py --dry-run
make clean         # remove __pycache__, .coverage, htmlcov/
```

---

## Notes

- `token.pickle` is saved after first login — delete it to force re-authentication
- Gmail API daily quota resets at midnight Pacific Time
- Emails in Trash are recoverable for 30 days via Gmail → Trash

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Please open an issue before large changes.

---

## License

MIT — free to use and modify.
