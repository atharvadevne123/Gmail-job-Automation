"""Run all three labeling scripts in sequence with a single authentication flow.

Usage:
    python scripts/run_all.py [--dry-run] [--log-level {DEBUG,INFO,WARNING,ERROR}]

This script authenticates once then sequentially runs:
  1. gmail_labeler   — labels rejections and applications
  2. label_interviews — labels interview invitations
"""

import argparse
import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import get_gmail_service, with_retry
from gmail_labeler import LABELS, get_or_create_label, label_threads
from label_interviews import (
    INTERVIEW_QUERIES,
    label_interview_threads,
)
from label_interviews import (
    LABEL_NAME as INTERVIEW_LABEL,
)
from label_interviews import (
    get_or_create_label as get_or_create_interview_label,
)

logger = logging.getLogger(__name__)


def run_all(dry_run: bool = False) -> dict:
    """Authenticate once and run all labeling passes.

    Args:
        dry_run: When ``True``, count matching threads without modifying them.

    Returns:
        A dict mapping label name to count of threads labeled.
    """
    logger.info("=" * 60)
    mode = "DRY RUN — no changes will be made" if dry_run else "Running all labelers"
    logger.info("  Gmail Job Automation — %s", mode)
    logger.info("=" * 60)

    logger.info("\nAuthenticating with Gmail...")
    service = get_gmail_service()
    logger.info("  Authenticated!\n")

    results: dict = {}

    existing_labels = with_retry(
        lambda: service.users().labels().list(userId='me').execute()
    ).get('labels', [])

    for label_name, queries in LABELS.items():
        label_id = get_or_create_label(service, label_name, existing_labels, dry_run=dry_run)
        count = label_threads(service, label_name, label_id, queries, dry_run=dry_run)
        results[label_name] = count

    interview_label_id = get_or_create_interview_label(
        service, INTERVIEW_LABEL, dry_run=dry_run
    )
    count = label_interview_threads(service, interview_label_id, dry_run=dry_run)
    results[INTERVIEW_LABEL] = count

    grand_total = sum(results.values())
    logger.info("\n" + "=" * 60)
    if dry_run:
        logger.info("  [dry-run] Would label %d emails in total.", grand_total)
    else:
        logger.info("  ALL DONE! %d emails labeled in total.", grand_total)
    logger.info("=" * 60)
    return results


def main() -> None:
    """Entry point for run_all script."""
    parser = argparse.ArgumentParser(
        description="Run all Gmail job labelers in sequence."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview counts without making any changes.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging verbosity (default: INFO).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(message)s",
    )
    run_all(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
