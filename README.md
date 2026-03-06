# 📬 Gmail Job Search Automation

**By [Atharva Devne](https://github.com/atharvadevne123)**

A collection of scripts to automatically organize your job search emails in Gmail — labels rejections, applications, and interviews, and moves them out of your inbox. Built to handle 14,000+ emails with no manual work.

---

## 📁 Files Overview

| File | Type | Description |
|------|------|-------------|
| `gmail_labeler.py` | Python | **Main script** — labels both rejections & applications. No time limit. Run on your computer. |
| `label_interviews.py` | Python | Labels all interview invitation emails into "Job Interviews" |
| `delete_job_emails.py` | Python | Permanently deletes all emails in Job Rejections & Job Applications Applied labels |
| `labelRejectionEmails.gs` | Google Apps Script | Labels rejection emails (auto-resumes every 6 min to beat quota) |
| `labelAppliedJobs.gs` | Google Apps Script | Labels application confirmation emails (auto-resumes every 6 min) |
| `gmail-rejection-labeler.html` | HTML | Browser-based tool with OAuth2 flow for labeling rejections |

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

**3. Add yourself as a test user**
- APIs & Services → OAuth consent screen → Test users → Add your Gmail

---

### Running the Scripts

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

## 📜 License

MIT — free to use and modify.
