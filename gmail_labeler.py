"""Label job-search emails in Gmail as rejections or applications."""
import argparse
import logging
import time
from typing import Any, Optional

from auth import get_gmail_service, with_retry

__all__ = ["get_or_create_label", "label_threads", "main", "LABELS"]

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

REJECTION_LABEL = "Job Rejections"
APPLICATION_LABEL = "Job Applications Applied"

LABELS: dict[str, list[str]] = {
    APPLICATION_LABEL: [
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
    REJECTION_LABEL: [
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
    ],
}

BATCH_SIZE: int = 100


def get_or_create_label(
    service: Any, name: str, existing_labels: list, dry_run: bool = False
) -> str:
    """Return label ID, creating the label if it does not exist."""
    for label in existing_labels:
        if label["name"] == name:
            logger.info("  Found existing label: %r", name)
            return label["id"]

    if dry_run:
        logger.info("  [dry-run] Would create label: %r", name)
        return f"dry_run_{name}"

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
    logger.info("  Created new label: %r", name)
    return label["id"]


def label_threads(
    service: Any,
    label_name: str,
    label_id: str,
    queries: list[str],
    dry_run: bool = False,
    batch_size: int = BATCH_SIZE,
) -> int:
    """Search for and label matching threads. Returns count labeled."""
    query = " OR ".join(queries)
    logger.info("Searching for %r (%d patterns)", label_name, len(queries))

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

        action = "would label" if dry_run else "labeling & archiving"
        logger.info("  Page %d: %d threads — %s...", page, len(threads), action)

        thread_ids = [t["id"] for t in threads]

        if dry_run:
            total += len(thread_ids)
            page_token = response.get("nextPageToken")
            if not page_token:
                break
            time.sleep(0.3)
            continue

        for i in range(0, len(thread_ids), batch_size):
            chunk = thread_ids[i : i + batch_size]
            errors: list[Exception] = []

            def _cb(req_id: str, response: Any, exception: Optional[Exception]) -> None:
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
                logger.warning("  %d threads failed in batch", len(errors))
            logger.info("  %d total labeled so far...", total)
            time.sleep(0.2)

        page_token = response.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.3)

    logger.info("%r — DONE! Total: %d labeled.", label_name, total)
    return total


def main() -> None:
    """Entry point for the Gmail job labeler."""
    parser = argparse.ArgumentParser(description="Label job-search emails in Gmail.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview how many emails would be labeled without making changes.",
    )
    args = parser.parse_args()
    dry_run: bool = args.dry_run

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger.info("=" * 60)
    mode = "DRY RUN" if dry_run else "Live"
    logger.info("  Gmail Job Labeler — %s", mode)
    logger.info("=" * 60)

    service = get_gmail_service()
    existing_labels = with_retry(
        lambda: service.users().labels().list(userId="me").execute()
    ).get("labels", [])

    grand_total = 0
    for label_name, queries in LABELS.items():
        label_id = get_or_create_label(service, label_name, existing_labels, dry_run=dry_run)
        count = label_threads(service, label_name, label_id, queries, dry_run=dry_run)
        grand_total += count

    logger.info("=" * 60)
    if dry_run:
        logger.info("  [dry-run] Would label %d emails total.", grand_total)
    else:
        logger.info("  ALL DONE! Grand total: %d emails labeled.", grand_total)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
