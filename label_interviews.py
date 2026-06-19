"""Label interview-invitation emails in Gmail under 'Job Interviews'.

Searches for invitation and scheduling keywords and applies the
"Job Interviews" label, archiving matches out of the inbox.
"""

import logging
import time
from typing import Any, Optional

from auth import get_gmail_service, with_retry

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
]

BATCH_SIZE = 100  # Google Batch API limit per HTTP request


def get_or_create_label(service: Any, name: str) -> str:
    """Return the Gmail label ID for *name*, creating the label if absent.

    Args:
        service: Authorised Gmail API service resource.
        name: Display name of the label to find or create.

    Returns:
        The label ID string.
    """
    results = with_retry(lambda: service.users().labels().list(userId='me').execute())
    for label in results.get('labels', []):
        if label['name'] == name:
            logger.info("Found existing label: '%s'", name)
            return label['id']

    label = with_retry(lambda: service.users().labels().create(
        userId='me',
        body={'name': name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    ).execute())
    logger.info("Created new label: '%s'", name)
    return label['id']


def label_interview_threads(service: Any, label_id: str) -> int:
    """Apply *label_id* to all interview-related threads and archive them.

    Paginates through Gmail search results using ``INTERVIEW_QUERIES``,
    processing matched threads in batches of ``BATCH_SIZE``.

    Args:
        service: Authorised Gmail API service resource.
        label_id: The label ID to apply to each matched thread.

    Returns:
        Total number of threads successfully labeled.
    """
    query = ' OR '.join(INTERVIEW_QUERIES)
    logger.info("Searching for interview emails (%d patterns)...", len(INTERVIEW_QUERIES))

    page_token = None
    page = 0
    total = 0

    while True:
        page += 1
        params: dict[str, Any] = {'userId': 'me', 'q': query, 'maxResults': 500}
        if page_token:
            params['pageToken'] = page_token

        response = with_retry(lambda p=params: service.users().threads().list(**p).execute())
        threads = response.get('threads', [])

        if not threads:
            break

        logger.info("Page %d: found %d threads — labeling & archiving...", page, len(threads))

        thread_ids = [t['id'] for t in threads]
        for i in range(0, len(thread_ids), BATCH_SIZE):
            chunk = thread_ids[i:i + BATCH_SIZE]
            errors: list[Exception] = []

            def _cb(req_id: str, response: Any, exception: Optional[Exception]) -> None:
                if exception:
                    errors.append(exception)

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
                logger.warning("%d threads failed in this batch", len(errors))
            logger.info("%d total labeled & moved out of inbox so far...", total)
            time.sleep(0.2)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

        time.sleep(0.3)

    logger.info("'%s' — DONE! Total: %d emails labeled.", LABEL_NAME, total)
    return total


def main() -> None:
    """Entry point: authenticate and label all interview-related threads."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logger.info("Gmail Interview Labeler - No Time Limits!")

    logger.info("Authenticating with Gmail...")
    service = get_gmail_service()
    logger.info("Authenticated!")

    label_id = get_or_create_label(service, LABEL_NAME)
    count = label_interview_threads(service, label_id)

    logger.info("ALL DONE! %d interview emails labeled.", count)


if __name__ == '__main__':
    main()
