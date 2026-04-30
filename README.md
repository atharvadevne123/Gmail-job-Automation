# 📬 Gmail Job Search Automation

![CI](https://github.com/atharvadevne123/Gmail-job-Automation/actions/workflows/ci.yml/badge.svg)

**By [Atharva Devne](https://github.com/atharvadevne123)**

A collection of scripts to automatically organize your job search emails in Gmail — labels rejections, applications, and interviews, and moves them out of your inbox. Built to handle 14,000+ emails with no manual work.

---

## 📁 Files Overview

| File | Type | Description |
|------|------|-------------|
| `gmail_labeler.py` | Python | **Main script** — labels both rejections & applications. No time limit. Run on your computer. |
| `label_interviews.py` | Python | Labels all interview invitation emails into "Job Interviews" |
| `delete_job_emails.py` | Python | Moves all emails in Job Rejections & Job Applications Applied labels to Trash |
| `.env.example` | Config | Template for `GMAIL_CREDENTIALS_PATH` and `GMAIL_TOKEN_PATH` env vars |
| `requirements.txt` | Config | All dependencies including pytest, pytest-cov, and ruff |
| `Makefile` | Config | Shortcuts: `make test`, `make lint`, `make fix`, `make clean` |

---

## 🏷️ Labels Created

- **Job Rejections** — emails where you were not selected
- **Job Applications Applied** — confirmation emails when you applied
- **Job Interviews** — emails inviting you to interview or asking screening questions

---

## 🐍 Python Scripts (Recommended — No Time Limits)

### Setup (One Time)

**1. Install dependencies**
```bash
pip3 install google-auth google-auth-oauthlib google-api-python-client
```

**2. Get credentials.json from Google Cloud**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. New Project → Enable **Gmail API**
3. Credentials → Create → **OAuth 2.0 Client ID** → Desktop app
4. Download JSON → rename to `credentials.json`
5. Place in same folder as the scripts

**3. (Optional) Override paths via environment variables**

Copy `.env.example` and set the paths if your files are not in the script directory:
```bash
cp .env.example .env
# Edit .env, then:
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
export GMAIL_TOKEN_PATH=/path/to/token.pickle
```

**4. Add yourself as a test user**
- APIs & Services → OAuth consent screen → Test users → Add your Gmail

---

### Running the Scripts

**Preview what would be labeled (no changes made):**
```bash
python3 gmail_labeler.py --dry-run
```

**Label rejections + applications (main script):**
```bash
python3 gmail_labeler.py
```

**Label interview emails:**
```bash
python3 label_interviews.py
```

**Permanently delete labeled emails (⚠️ irreversible):**
```bash
python3 delete_job_emails.py
```

**Keep Mac awake while running:**
```bash
caffeinate -i python3 gmail_labeler.py
```

---

## 📝 Google Apps Script (Alternative)

> ⚠️ Apps Script has a **6-minute execution limit** and a **daily quota**. The scripts auto-resume every minute to work around the time limit, but may hit quota on large inboxes. Use the Python scripts for best results.

**Setup:**
1. Go to [script.google.com](https://script.google.com)
2. New Project → paste the `.gs` file contents
3. Click **Run** → approve permissions
4. Scripts auto-resume until all emails are processed

---

## 🔑 Rejection Keywords Detected

Scripts scan for these phrases found across real rejection emails:

```
"not be moving forward" | "regret to inform" | "narrowed the search"
"pursue other applicants" | "move forward with other candidates"
"not advance your candidacy" | "move forward with another candidate"
"not proceeding with your candidacy" | "the role has been filled"
"other candidates whose qualifications" | "more closely match"
"not selected for" | "unfortunately will not" | "decided not to move forward"
"chosen to move forward with" | "no longer being considered"
```

---

## 📊 Interview Keywords Detected

```
"invitation to interview" | "interview invitation" | "schedule your interview"
"first step in our interview process" | "answer a few follow-up questions"
"pre-interview form" | "instant interview" | "webex link for your upcoming interview"
"advance to the next stage" | "next round of interviews"
```

---

## ⚠️ Notes

- Scripts require Gmail API OAuth2 credentials (free)
- `token.pickle` is saved after first login — delete it to re-authenticate
- Permanently deleted emails cannot be recovered
- Daily Gmail API quota resets at midnight Pacific Time

---

## 🧪 Testing

The project includes a pytest suite that mocks all Gmail API calls — no credentials required to run tests.

**Install dependencies and run:**
```bash
pip install -r requirements.txt
python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing
# or via Makefile:
make test
```

**Test coverage (27 tests total):**
- `tests/test_auth.py` — `with_retry()` backoff, network error retry, `get_gmail_service` credential handling (11 tests)
- `tests/test_labeler.py` — label lookup/creation, thread pagination, `--dry-run` mode (7 tests)
- `tests/test_delete.py` — label ID lookup and batch trash operations (5 tests)
- `tests/test_label_interviews.py` — interview label creation and thread labeling (4 tests)

**Dev shortcuts (Makefile):**
```bash
make install   # pip install -r requirements.txt
make test      # pytest with coverage
make lint      # ruff check
make fix       # ruff --fix
make clean     # remove __pycache__, .coverage, etc.
```

---

## 📜 License

MIT — free to use and modify.
