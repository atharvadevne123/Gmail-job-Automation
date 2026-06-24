"""Count emails in Gmail labels without modifying them."""
from __future__ import annotations

import argparse
import logging

from auth import get_gmail_service
from utils import format_count

__all__ = ["count_label", "main"]

logging.getLogger(__name__).addHandler(logging.NullHandler())

LABELS_TO_COUNT = [
    "Job Rejections",
    "Job Applications Applied",
    "Interview Invitations",
]


def count_label(service: object, label_name: str) -> int:
    """Return the total thread count for a label."""
    all_labels = service.users().labels().list(userId="me").execute().get("labels", [])
    label_id = next((lb["id"] for lb in all_labels if lb["name"] == label_name), None)
    if label_id is None:
        logging.getLogger(__name__).warning("Label %r not found", label_name)
        return 0
    info = service.users().labels().get(userId="me", id=label_id).execute()
    return int(info.get("threadsTotal", 0))


def main() -> None:
    """Count threads in job-related Gmail labels."""
    parser = argparse.ArgumentParser(description="Count emails in job labels")
    parser.add_argument("--label", help="Specific label to count (default: all)")
    args = parser.parse_args()
    service = get_gmail_service()
    targets = [args.label] if args.label else LABELS_TO_COUNT
    for name in targets:
        n = count_label(service, name)
        print(format_count(n, "thread"), f"in {name!r}")


if __name__ == "__main__":
    main()
