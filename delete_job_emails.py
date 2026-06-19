"""Move job-search labeled emails to Gmail Trash and remove the labels.

Iterates over the "Job Rejections" and "Job Applications Applied" labels,
trashing all threads in batches and then deleting each label. Emails are
recoverable from Trash for 30 days.
"""

import logging
import time
from typing import Any, Optional

from auth import get_gmail_service, with_retry

logger = logging.getLogger(__name__)

LABELS_TO_TRASH = [
    "Job Rejections",
    "Job Applications Applied"
]

BATCH_SIZE = 100  # Google Batch API limit per HTTP request


def get_label_id(service: Any, name: str) -> Optional[str]:
    results = with_retry(lambda: service.users().labels().list(userId='me').execute())
    for label in results.get('labels', []):
        if label['name'] == name:
            return label['id']
    return None


def trash_all_in_label(service: Any, label_name: str, label_id: str) -> int:
    logger.info("\n🗑️  Moving all emails in '%s' to Trash...", label_name)
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

        logger.info("  Page %d: trashing %d threads...", page, len(threads))

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
                logger.warning("    ⚠️  %d threads failed in this batch", len(errors))
            if total % 50 == 0:
                logger.info("    🗑️  %d moved to Trash so far...", total)
            time.sleep(0.1)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    with_retry(lambda: service.users().labels().delete(userId='me', id=label_id).execute())
    logger.info("  ✅ '%s' — %d emails moved to Trash + label removed!\n", label_name, total)
    return total


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger.info("=" * 60)
    logger.info("  🗑️  Gmail Job Emails — Move to Trash")
    logger.info("  The following labels will be emptied and removed:")
    for label in LABELS_TO_TRASH:
        logger.info("    - %s", label)
    logger.info("  Emails are recoverable for 30 days from Gmail → Trash.")
    logger.info("=" * 60)

    confirm = input("\n  Type YES (uppercase) to confirm: ")
    if confirm.strip().upper() != "YES":
        logger.info("  Cancelled. Nothing was changed.")
        return

    logger.info("\n🔐 Authenticating...")
    service = get_gmail_service()
    logger.info("  ✓ Authenticated!\n")

    grand_total = 0
    for label_name in LABELS_TO_TRASH:
        label_id = get_label_id(service, label_name)
        if not label_id:
            logger.warning("  ⚠️  Label '%s' not found — skipping.", label_name)
            continue
        count = trash_all_in_label(service, label_name, label_id)
        grand_total += count

    logger.info("=" * 60)
    logger.info("  🎉 ALL DONE! %d emails moved to Trash.", grand_total)
    logger.info("  To permanently delete: Gmail → Trash → Empty Trash")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
