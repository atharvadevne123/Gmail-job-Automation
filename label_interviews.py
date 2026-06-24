"""Label interview invitation emails in Gmail."""
from __future__ import annotations

import argparse
import logging
import time
from typing import Any, Optional

from auth import get_gmail_service, with_retry

__all__ = ["get_or_create_label", "label_interview_threads", "main"]

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

LABEL_NAME = "Job Interviews"

INTERVIEW_QUERIES: list[str] = [
    '"invitation to interview"',
    '"interview invitation"',
    '"schedule your interview"',
    '"first step in our interview process"',
    '"answer a few follow-up questions"',
    '"pre-interview form"',
    '"instant interview"',
    '"webex link for your upcoming interview"',
    '"advance to the next stage"',
    '"next round of interviews"',
    '"phone screen"',
    '"video interview"',
    '"we would like to invite you"',
    '"we are pleased to invite you"',
    '"would you be available for"',
    '"schedule a call"',
    '"technical interview"',
    '"hiring manager would like to connect"',
    'subject:"interview"',
    '"excited to move you forward"',
    '"move you to the next step"',
    '"onsite interview"',
    '"coding challenge"',
    '"take-home assessment"',
]

BATCH_SIZE = 100


def get_or_create_label(service: Any, name: str) -> str:
    """Return label ID, creating it if absent."""
    results = with_retry(lambda: service.users().labels().list(userId="me").execute())
    for label in results.get("labels", []):
        if label["name"] == name:
            logger.info("Found existing label: %r", name)
            return label["id"]

    label = with_retry(
        lambda: service.users()
        .labels()
        .create(
            userId="me",
            body={
                "name": name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        .execute()
    )
    logger.info("Created new label: %r", name)
    return label["id"]


def label_interview_threads(
    service: Any, label_id: str, dry_run: bool = False
) -> int:
    """Label and archive all interview-related threads. Returns count labeled."""
    query = " OR ".join(INTERVIEW_QUERIES)
    logger.info("Searching for interview emails (%d patterns)...", len(INTERVIEW_QUERIES))

    page_token: Optional[str] = None
    page = 0
    total = 0

    while True:
        page += 1
        params: dict[str, Any] = {"userId": "me", "q": query, "maxResults": 500}
        if page_token:
            params["pageToken"] = page_token

        response = with_retry(lambda p=params: service.users().threads().list(**p).execute())
        threads = response.get("threads", [])

        if not threads:
            break

        logger.info("Page %d: found %d threads", page, len(threads))
        thread_ids = [t["id"] for t in threads]

        if dry_run:
            total += len(thread_ids)
            page_token = response.get("nextPageToken")
            if not page_token:
                break
            time.sleep(0.3)
            continue

        for i in range(0, len(thread_ids), BATCH_SIZE):
            chunk = thread_ids[i : i + BATCH_SIZE]
            errors: list[Exception] = []

            def _cb(req_id: str, resp: Any, exception: Optional[Exception]) -> None:
                if exception:
                    errors.append(exception)

            batch = service.new_batch_http_request(callback=_cb)
            for tid in chunk:
                batch.add(
                    service.users()
                    .threads()
                    .modify(
                        userId="me",
                        id=tid,
                        body={"addLabelIds": [label_id], "removeLabelIds": ["INBOX"]},
                    )
                )
            with_retry(batch.execute)

            total += len(chunk) - len(errors)
            if errors:
                logger.warning("%d threads failed in batch", len(errors))
            logger.info("%d total labeled so far...", total)
            time.sleep(0.2)

        page_token = response.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.3)

    logger.info("%r — DONE! Total: %d labeled.", LABEL_NAME, total)
    return total


def main() -> None:
    """Entry point for the interview labeler."""
    parser = argparse.ArgumentParser(description="Label interview emails in Gmail.")
    parser.add_argument("--dry-run", action="store_true", help="Preview without changes.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger.info("Gmail Interview Labeler — %s", "DRY RUN" if args.dry_run else "Live")

    service = get_gmail_service()
    label_id = get_or_create_label(service, LABEL_NAME)
    count = label_interview_threads(service, label_id, dry_run=args.dry_run)
    logger.info("ALL DONE! %d interview emails labeled.", count)


if __name__ == "__main__":
    main()
