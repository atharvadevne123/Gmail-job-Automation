# ============================================================
#  Gmail Job Emails — Move to Trash
#  Moves all emails under:
#  - "Job Rejections"
#  - "Job Applications Applied"
#  to Trash. Recoverable for 30 days via Gmail → Trash.
#  To permanently delete immediately: Gmail → Trash → Empty Trash
# ============================================================

import time
from auth import get_gmail_service, with_retry

LABELS_TO_TRASH = [
    "Job Rejections",
    "Job Applications Applied"
]

BATCH_SIZE = 100  # Google Batch API limit per HTTP request


def get_label_id(service, name):
    results = with_retry(lambda: service.users().labels().list(userId='me').execute())
    for label in results.get('labels', []):
        if label['name'] == name:
            return label['id']
    return None


def trash_all_in_label(service, label_name, label_id):
    print(f"\n🗑️  Moving all emails in '{label_name}' to Trash...")
    page_token = None
    page = 0
    total = 0

    while True:
        page += 1
        params = {'userId': 'me', 'labelIds': [label_id], 'maxResults': 500}
        if page_token:
            params['pageToken'] = page_token

        response = with_retry(lambda p=params: service.users().threads().list(**p).execute())
        threads = response.get('threads', [])

        if not threads:
            break

        print(f"  Page {page}: trashing {len(threads)} threads...")

        thread_ids = [t['id'] for t in threads]
        for i in range(0, len(thread_ids), BATCH_SIZE):
            chunk = thread_ids[i:i + BATCH_SIZE]
            errors = []

            def _cb(req_id, response, exception):
                if exception:
                    errors.append(exception)

            batch = service.new_batch_http_request(callback=_cb)
            for tid in chunk:
                batch.add(service.users().threads().trash(userId='me', id=tid))
            with_retry(batch.execute)

            total += len(chunk) - len(errors)
            if errors:
                print(f"    ⚠️  {len(errors)} threads failed in this batch")
            if total % 50 == 0:
                print(f"    🗑️  {total} moved to Trash so far...")
            time.sleep(0.1)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    with_retry(lambda: service.users().labels().delete(userId='me', id=label_id).execute())
    print(f"  ✅ '{label_name}' — {total} emails moved to Trash + label removed!\n")
    return total


def main():
    print("=" * 60)
    print("  🗑️  Gmail Job Emails — Move to Trash")
    print("  The following labels will be emptied and removed:")
    for label in LABELS_TO_TRASH:
        print(f"    - {label}")
    print("  Emails are recoverable for 30 days from Gmail → Trash.")
    print("=" * 60)

    confirm = input("\n  Type YES to confirm: ")
    if confirm.strip() != "YES":
        print("  Cancelled. Nothing was changed.")
        return

    print("\n🔐 Authenticating...")
    service = get_gmail_service()
    print("  ✓ Authenticated!\n")

    grand_total = 0
    for label_name in LABELS_TO_TRASH:
        label_id = get_label_id(service, label_name)
        if not label_id:
            print(f"  ⚠️  Label '{label_name}' not found — skipping.")
            continue
        count = trash_all_in_label(service, label_name, label_id)
        grand_total += count

    print("=" * 60)
    print(f"  🎉 ALL DONE! {grand_total} emails moved to Trash.")
    print("  To permanently delete: Gmail → Trash → Empty Trash")
    print("=" * 60)


if __name__ == '__main__':
    main()
