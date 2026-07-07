"""Label job-search emails in Gmail as rejections or applications.

Searches your Gmail inbox for keyword patterns and applies the labels
"Job Rejections" and "Job Applications Applied", archiving matched
threads out of the inbox in batched API calls. Supports --dry-run
mode to preview counts without making changes.
"""

import argparse
import logging
import time
from typing import Any, Optional

from auth import get_gmail_service, with_retry

logger = logging.getLogger(__name__)

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

BATCH_SIZE = 100  # Google Batch API limit per HTTP request


def get_or_create_label(service: Any, name: str, existing_labels: list, dry_run: bool = False) -> str:
    """Return the ID of a Gmail label, creating it if absent.

    Args:
        service: Authorised Gmail API service resource.
        name: Display name of the label to find or create.
        existing_labels: List of label dicts already fetched from the API
            (each must have ``'name'`` and ``'id'`` keys).
        dry_run: When ``True``, skip the API create call and return a
            placeholder ID prefixed with ``'dry_run_'``.

    Returns:
        The label ID string.
    """
    for label in existing_labels:
        if label['name'] == name:
            logger.info("  ✓ Found existing label: '%s'", name)
            return label['id']

    if dry_run:
        logger.info("  [dry-run] Would create label: '%s'", name)
        return f"dry_run_{name}"

    label = with_retry(lambda: service.users().labels().create(
        userId='me',
        body={'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    ).execute())
    logger.info("  ✓ Created new label: '%s'", name)
    return label['id']


def label_threads(service: Any, label_name: str, label_id: str, queries: list, dry_run: bool = False) -> int:
    """Search Gmail for threads matching any query pattern and apply a label.

    Paginates through all results (up to 500 threads per page), applies
    *label_id* and removes the INBOX label from each thread in batches of
    ``BATCH_SIZE``.

    Args:
        service: Authorised Gmail API service resource.
        label_name: Human-readable label name used only for log messages.
        label_id: The label ID returned by :func:`get_or_create_label`.
        queries: List of Gmail query strings joined with ``OR``.
        dry_run: When ``True``, count matching threads but do not modify them.

    Returns:
        Total number of threads successfully labeled (or that would have been
        labeled in dry-run mode).
    """
    query = ' OR '.join(queries)
    logger.info("\n🔍 Searching for: '%s'", label_name)
    logger.info("   Query has %d keyword patterns\n", len(queries))

    page_token = None
    page = 0
    total = 0

    while True:
        page += 1
        params = {'userId': 'me', 'q': query, 'maxResults': 500}
        if page_token:
            params['pageToken'] = page_token

        response = with_retry(lambda p=params: service.users().threads().list(**p).execute())
        threads = response.get('threads', [])

        if not threads:
            break

        action = "would label" if dry_run else "labeling & archiving"
        logger.info("  Page %d: found %d threads — %s...", page, len(threads), action)

        thread_ids = [t['id'] for t in threads]

        if dry_run:
            total += len(thread_ids)
            logger.info("    [dry-run] %d total would be labeled so far...", total)
            page_token = response.get('nextPageToken')
            if not page_token:
                break
            time.sleep(0.3)
            continue

        for i in range(0, len(thread_ids), BATCH_SIZE):
            chunk = thread_ids[i:i + BATCH_SIZE]
            errors: list[Exception] = []

            def _cb(
                req_id: str,
                response: Any,
                exception: Optional[Exception],
                _errors: list = errors,
            ) -> None:
                if exception:
                    _errors.append(exception)

            batch = service.new_batch_http_request(callback=_cb)
            for tid in chunk:
                batch.add(service.users().threads().modify(
                    userId='me',
                    id=tid,
                    body={'addLabelIds': [label_id], 'removeLabelIds': ['INBOX']}
                ))
            with_retry(batch.execute)

            total += len(chunk) - len(errors)
            if errors:
                logger.warning("    ⚠️  %d threads failed in this batch", len(errors))
            logger.info("    ✓ %d total labeled & moved out of inbox so far...", total)
            time.sleep(0.2)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

        time.sleep(0.3)

    logger.info("\n  ✅ '%s' — DONE! Total: %d emails labeled.\n", label_name, total)
    return total


def main() -> None:
    """Entry point: authenticate, create labels, and process all query groups."""
    parser = argparse.ArgumentParser(description="Label job-search emails in Gmail.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview how many emails would be labeled without making any changes.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set the logging verbosity level (default: INFO).",
    )
    args = parser.parse_args()
    dry_run: bool = args.dry_run

    logging.basicConfig(level=getattr(logging, args.log_level), format='%(message)s')
    logger.info("=" * 60)
    if dry_run:
        logger.info("  Gmail Job Labeler — DRY RUN (no changes will be made)")
    else:
        logger.info("  Gmail Job Labeler — No Time Limits!")
    logger.info("=" * 60)

    logger.info("\n🔐 Authenticating with Gmail...")
    service = get_gmail_service()
    logger.info("  ✓ Authenticated!\n")

    existing_labels = with_retry(
        lambda: service.users().labels().list(userId='me').execute()
    ).get('labels', [])

    grand_total = 0
    for label_name, queries in LABELS.items():
        label_id = get_or_create_label(service, label_name, existing_labels, dry_run=dry_run)
        count = label_threads(service, label_name, label_id, queries, dry_run=dry_run)
        grand_total += count

    logger.info("=" * 60)
    if dry_run:
        logger.info("  [dry-run] Would label %d emails total. Run without --dry-run to apply.", grand_total)
    else:
        logger.info("  🎉 ALL DONE! Grand total: %d emails labeled.", grand_total)
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
