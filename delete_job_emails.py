# ============================================================
#  Gmail Job Emails DELETER
#  Permanently deletes all emails under:
#  - "Job Rejections"
#  - "Job Applications Applied"
#  ⚠️ THIS CANNOT BE UNDONE
# ============================================================

import os
import time
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import webbrowser

webbrowser.register('safari', None, webbrowser.BackgroundBrowser('/Applications/Safari.app'))

SCOPES = ['https://mail.google.com/']

LABELS_TO_DELETE = [
    "Job Rejections",
    "Job Applications Applied"
]

def get_gmail_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, browser='safari')
        with open('token.pickle', 'wb') as f:
            pickle.dump(creds, f)
    return build('gmail', 'v1', credentials=creds)


def get_label_id(service, name):
    results = service.users().labels().list(userId='me').execute()
    for label in results.get('labels', []):
        if label['name'] == name:
            return label['id']
    return None


def delete_all_in_label(service, label_name, label_id):
    print(f"\n🗑️  Deleting all emails in '{label_name}'...")
    page_token = None
    page = 0
    total = 0

    while True:
        page += 1
        params = {
            'userId': 'me',
            'labelIds': [label_id],
            'maxResults': 500
        }
        if page_token:
            params['pageToken'] = page_token

        response = service.users().threads().list(**params).execute()
        threads = response.get('threads', [])

        if not threads:
            break

        print(f"  Page {page}: deleting {len(threads)} threads...")

        for thread in threads:
            service.users().threads().delete(
                userId='me',
                id=thread['id']
            ).execute()
            total += 1
            if total % 50 == 0:
                print(f"    🗑️  {total} deleted so far...")
            time.sleep(0.1)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    # Delete the label itself
    service.users().labels().delete(userId='me', id=label_id).execute()
    print(f"  ✅ '{label_name}' — {total} emails deleted + label removed!\n")
    return total


def main():
    print("=" * 60)
    print("  ⚠️  Gmail Job Emails DELETER")
    print("  This will permanently delete all emails in:")
    for l in LABELS_TO_DELETE:
        print(f"    - {l}")
    print("=" * 60)

    confirm = input("\n  Type YES to confirm permanent deletion: ")
    if confirm.strip() != "YES":
        print("  Cancelled. Nothing was deleted.")
        return

    print("\n🔐 Authenticating...")
    service = get_gmail_service()
    print("  ✓ Authenticated!\n")

    grand_total = 0
    for label_name in LABELS_TO_DELETE:
        label_id = get_label_id(service, label_name)
        if not label_id:
            print(f"  ⚠️  Label '{label_name}' not found — skipping.")
            continue
        count = delete_all_in_label(service, label_name, label_id)
        grand_total += count

    print("=" * 60)
    print(f"  🎉 ALL DONE! {grand_total} emails permanently deleted.")
    print("  They will be permanently deleted after 30 days.")
    print("  To delete immediately: go to Gmail → Trash → Empty Trash")
    print("=" * 60)


if __name__ == '__main__':
    main()
