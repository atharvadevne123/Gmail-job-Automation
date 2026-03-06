# ============================================================
#  Gmail Job Labeler — runs on your computer, NO time limits
#  Labels ALL rejection + application emails in one go
#
#  SETUP (one time):
#  1. pip install google-auth google-auth-oauthlib google-api-python-client
#  2. Get credentials.json from Google Cloud Console (see README below)
#  3. Run: python gmail_labeler.py
# ============================================================

import os
import time
import pickle
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Force Safari as the browser
webbrowser.register('safari', None, webbrowser.BackgroundBrowser('/Applications/Safari.app'))

# ── SCOPES ──────────────────────────────────────────────────
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# ── LABELS TO CREATE ────────────────────────────────────────
LABELS = {
    "Job Applications Applied": [
        'subject:"thank you for applying"',
        'subject:"thanks for applying"',
        'subject:"thank you for your application"',
        'subject:"application received"',
        'subject:"application submitted"',
        'subject:"application confirmation"',
        'subject:"we received your application"',
        'subject:"successfully submitted application"',
        'subject:"your application for"',
        '"your application has been received"',
        '"we have received your application"',
        '"application has been successfully submitted"',
        '"successfully submitted your application"',
        '"application is currently under review"',
        '"will review your application"',
        '"we will carefully review your application"',
        '"your resume will be considered"',
        '"application is officially in our system"',
        '"thank you for submitting your application"',
        '"thank you for expressing an interest"',
        '"will be reviewed by a member"',
        '"if your skills and experience align"',
        '"if your qualifications match"',
        '"if you are selected for an interview"',
        '"team will reach out to discuss next steps"',
        '"recruiting team will contact you"',
    ],
    "Job Rejections": [
        '"not be moving forward"',
        '"not moving forward"',
        '"will not be moving"',
        '"regret to inform"',
        '"narrowed the search"',
        '"pursue other applicants"',
        '"pursuing other applicants"',
        '"move forward with other candidates"',
        '"progress with other candidates"',
        '"decided to move forward with other"',
        '"not advance your candidacy"',
        '"not advancing your candidacy"',
        '"move forward with another candidate"',
        '"decided to move forward with another"',
        '"not proceeding with your candidacy"',
        '"decided to continue to pursue other"',
        '"not continue the process"',
        '"at this time we are pursuing other"',
        '"the role has been filled"',
        '"filled the position"',
        '"position has been filled"',
        '"will not be pursuing you"',
        '"not be pursuing you"',
        '"other candidates whose qualifications"',
        '"more closely match"',
        '"not selected for"',
        '"unfortunately will not"',
        '"decided not to move forward"',
        '"chosen to move forward with"',
        '"have chosen another"',
        '"no longer being considered"',
        '"not the right fit"',
        '"have decided not to"',
        '"unable to offer you"',
        '"not be able to offer"',
    ]
}

# ── AUTH ─────────────────────────────────────────────────────
def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("\n❌ ERROR: credentials.json not found!")
                print("   Follow the setup steps in the README at the bottom of this file.\n")
                exit(1)
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, browser="safari")
        with open('token.pickle', 'wb') as f:
            pickle.dump(creds, f)

    return build('gmail', 'v1', credentials=creds)


# ── GET OR CREATE LABEL ───────────────────────────────────────
def get_or_create_label(service, name):
    results = service.users().labels().list(userId='me').execute()
    for label in results.get('labels', []):
        if label['name'] == name:
            print(f"  ✓ Found existing label: '{name}'")
            return label['id']

    label = service.users().labels().create(userId='me', body={
        'name': name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }).execute()
    print(f"  ✓ Created new label: '{name}'")
    return label['id']


# ── SEARCH + LABEL ALL MATCHING THREADS ──────────────────────
def label_threads(service, label_name, label_id, queries):
    query = ' OR '.join(queries)
    print(f"\n🔍 Searching for: '{label_name}'")
    print(f"   Query has {len(queries)} keyword patterns\n")

    page_token = None
    page = 0
    total = 0

    while True:
        page += 1
        params = {
            'userId': 'me',
            'q': query,
            'maxResults': 500,
        }
        if page_token:
            params['pageToken'] = page_token

        response = service.users().threads().list(**params).execute()
        threads = response.get('threads', [])

        if not threads:
            break

        print(f"  Page {page}: found {len(threads)} threads — labeling & archiving...")

        # Batch modify in chunks of 1000 (Gmail API limit)
        chunk_size = 1000
        for i in range(0, len(threads), chunk_size):
            chunk = threads[i:i + chunk_size]
            ids = [t['id'] for t in chunk]
            for thread_id in ids:
                service.users().threads().modify(
                    userId='me',
                    id=thread_id,
                    body={
                        'addLabelIds': [label_id],
                        'removeLabelIds': ['INBOX']
                    }
                ).execute()
            total += len(ids)
            print(f"    ✓ {total} total labeled & moved out of inbox so far...")
            time.sleep(0.2)  # gentle rate limiting

        page_token = response.get('nextPageToken')
        if not page_token:
            break

        time.sleep(0.3)

    print(f"\n  ✅ '{label_name}' — DONE! Total: {total} emails labeled.\n")
    return total


# ── MAIN ─────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Gmail Job Labeler — No Time Limits!")
    print("=" * 60)

    print("\n🔐 Authenticating with Gmail...")
    service = get_gmail_service()
    print("  ✓ Authenticated!\n")

    grand_total = 0
    for label_name, queries in LABELS.items():
        label_id = get_or_create_label(service, label_name)
        count = label_threads(service, label_name, label_id, queries)
        grand_total += count

    print("=" * 60)
    print(f"  🎉 ALL DONE! Grand total: {grand_total} emails labeled.")
    print("=" * 60)


if __name__ == '__main__':
    main()


# ============================================================
#  README — ONE-TIME SETUP (takes ~3 minutes)
# ============================================================
#
#  STEP 1 — Install dependencies
#  Open terminal in VS Code and run:
#
#    pip install google-auth google-auth-oauthlib google-api-python-client
#
#  STEP 2 — Get credentials.json from Google Cloud
#
#    1. Go to https://console.cloud.google.com
#    2. Create a new project (or use existing)
#    3. Go to "APIs & Services" → "Enable APIs"
#    4. Search for "Gmail API" → Enable it
#    5. Go to "APIs & Services" → "Credentials"
#    6. Click "Create Credentials" → "OAuth 2.0 Client ID"
#    7. Application type: "Desktop app" → Create
#    8. Download the JSON file
#    9. Rename it to: credentials.json
#   10. Put it in the SAME folder as this script
#
#  STEP 3 — Run the script
#
#    python gmail_labeler.py
#
#    A browser window will open asking you to sign in to Google.
#    Click "Allow" — then come back to VS Code.
#    The script runs until ALL emails are labeled. No time limit!
#
#  NOTE: token.pickle is saved after first login so you won't
#  need to sign in again next time you run it.
# ============================================================
