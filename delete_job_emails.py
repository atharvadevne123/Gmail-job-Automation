"""Move labeled job emails to Gmail Trash."""
from __future__ import annotations

import argparse
import logging
import time
from typing import Any, Optional

from auth import get_gmail_service, with_retry

__all__ = ["get_label_id", "trash_all_in_label", "main"]

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

LABELS_TO_TRASH = [
    "Job Rejections",
    "Job Applications Applied",
]

BATCH_SIZE = 100


def get_label_id(service: Any, name: str) -> Optional[str]:
    """Return the ID of a label by name, or None if not found."""
    results = with_retry(lambda: service.users().labels().list(userId="me").execute())
    for label in results.get("labels", []):
        if label["name"] == name:
            return label["id"]
    return None


def trash_all_in_label(
    service: Any, label_name: str, label_id: str, dry_run: bool = False
) -> int:
    """Move all threads in label to Trash and delete the label. Returns count moved."""
    logger.info("Moving all emails in %r to Trash...", label_name)
    page_token: Optional[str] = None
    page = 0
    total = 0
    batch_errors = 0

    while True:
        page += 1
        params: dict[str, Any] = {
            "userId": "me",
            "labelIds": [label_id],
            "maxResults": 500,
        }
        if page_token:
            params["pageToken"] = page_token

        response = with_retry(lambda p=params: service.users().threads().list(**p).execute())
        threads = response.get("threads", [])

        if not threads:
            break

        logger.info("  Page %d: processing %d threads...", page, len(threads))

        if dry_run:
            total += len(threads)
            page_token = response.get("nextPageToken")
            if not page_token:
                break
            continue

        thread_ids = [t["id"] for t in threads]
        for i in range(0, len(thread_ids), BATCH_SIZE):
            chunk = thread_ids[i : i + BATCH_SIZE]
            errors: list[Exception] = []

            def _cb(req_id: str, resp: Any, exception: Optional[Exception]) -> None:
                if exception:
                    errors.append(exception)

            batch = service.new_batch_http_request(callback=_cb)
            for tid in chunk:
                batch.add(service.users().threads().trash(userId="me", id=tid))
            with_retry(batch.execute)

            total += len(chunk) - len(errors)
            batch_errors += len(errors)
            if errors:
                logger.warning("  %d threads failed in batch", len(errors))
            logger.info("  %d moved to Trash so far...", total)
            time.sleep(0.1)

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    if not dry_run:
        with_retry(lambda: service.users().labels().delete(userId="me", id=label_id).execute())
        logger.info(
            "%r — %d trashed, %d errors, label removed.", label_name, total, batch_errors
        )
    else:
        logger.info("[dry-run] Would trash %d emails in %r.", total, label_name)
    return total


def main() -> None:
    """Entry point for moving job emails to Trash."""
    parser = argparse.ArgumentParser(description="Move job emails to Gmail Trash.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("=" * 60)
    logger.info("  Gmail Job Emails — Move to Trash")
    for label in LABELS_TO_TRASH:
        logger.info("    - %s", label)
    logger.info("=" * 60)

    if not args.dry_run:
        confirm = input("
  Type YES (uppercase) to confirm: ")
        if confirm.strip().upper() != "YES":
            logger.info("  Cancelled.")
            return

    service = get_gmail_service()

    summary: dict[str, int] = {}
    for label_name in LABELS_TO_TRASH:
        label_id = get_label_id(service, label_name)
        if not label_id:
            logger.warning("  Label %r not found — skipping.", label_name)
            continue
        count = trash_all_in_label(service, label_name, label_id, dry_run=args.dry_run)
        summary[label_name] = count

    grand_total = sum(summary.values())
    logger.info("=" * 60)
    for name, n in summary.items():
        logger.info("  %-35s %5d", name, n)
    logger.info("-" * 60)
    if args.dry_run:
        logger.info("  [dry-run] Would trash %d emails total.", grand_total)
    else:
        logger.info("  ALL DONE! %d emails moved to Trash.", grand_total)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
