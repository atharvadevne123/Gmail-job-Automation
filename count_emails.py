"""Count emails in Gmail labels without modifying them."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys

from auth import get_gmail_service
from utils import format_count

__all__ = ["count_label", "count_all", "export_csv", "main"]

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


def count_all(service: object, labels: list[str]) -> dict[str, int]:
    """Return a mapping of label name -> thread count."""
    return {name: count_label(service, name) for name in labels}


def export_csv(counts: dict[str, int], output: object = sys.stdout) -> None:
    """Write label counts as CSV to the given output stream."""
    writer = csv.writer(output)
    writer.writerow(["label", "threads"])
    for name, n in counts.items():
        writer.writerow([name, n])


def main() -> None:
    """Count threads in job-related Gmail labels."""
    parser = argparse.ArgumentParser(description="Count emails in job labels")
    parser.add_argument("--label", help="Specific label to count (default: all)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--csv", action="store_true", help="Output as CSV")
    args = parser.parse_args()
    service = get_gmail_service()
    targets = [args.label] if args.label else LABELS_TO_COUNT
    counts = count_all(service, targets)

    if args.json:
        json.dump(counts, sys.stdout, indent=2)
        print()
    elif args.csv:
        export_csv(counts)
    else:
        for name, n in counts.items():
            print(format_count(n, "thread"), f"in {name!r}")


if __name__ == "__main__":
    main()
