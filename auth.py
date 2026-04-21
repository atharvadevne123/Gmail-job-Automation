import os
import pickle
import time
import webbrowser

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

webbrowser.register('safari', None, webbrowser.BackgroundBrowser('/Applications/Safari.app'))

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, 'token.pickle')
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')


def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print("\n❌ ERROR: credentials.json not found!")
                print("   Follow the setup steps in the README.\n")
                exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0, browser='safari')
        with open(TOKEN_PATH, 'wb') as f:
            pickle.dump(creds, f)

    return build('gmail', 'v1', credentials=creds)


def with_retry(fn, max_retries=5):
    """Call fn() with exponential backoff on transient API errors (429/500/503)."""
    for attempt in range(max_retries):
        try:
            return fn()
        except HttpError as e:
            if e.resp.status in (429, 500, 503) and attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"  ⏳ API error {e.resp.status}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
