"""Gmail authentication and retry utilities.

Usage::

    from auth import get_gmail_service, with_retry

    service = get_gmail_service()
    result = with_retry(lambda: service.users().labels().list(userId="me").execute())
"""
from __future__ import annotations

import logging
import os
import pickle
import time
from typing import Any, Callable

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

__all__ = ["get_gmail_service", "with_retry", "is_authenticated"]

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)

# gmail.modify allows reading, labeling, and moving but not permanently deleting.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.environ.get("GMAIL_TOKEN_PATH", os.path.join(BASE_DIR, "token.pickle"))
CREDENTIALS_PATH = os.environ.get(
    "GMAIL_CREDENTIALS_PATH", os.path.join(BASE_DIR, "credentials.json")
)


def is_authenticated() -> bool:
    """Return True if a valid, non-expired token exists on disk."""
    if not os.path.exists(TOKEN_PATH):
        return False
    try:
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
        return bool(creds and creds.valid)
    except Exception:
        return False


def get_gmail_service() -> Any:
    """Authenticate and return an authorized Gmail API service object.

    On first run, opens a browser for OAuth consent. On subsequent runs,
    loads the cached token from TOKEN_PATH. Refreshes expired tokens
    automatically. Raises FileNotFoundError if credentials.json is missing.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                logger.warning("Token refresh failed; re-authenticating.")
                creds = None

        if not creds:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_PATH}. "
                    "Follow the setup steps in the README."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)


_TRANSIENT_NETWORK_ERRORS = (OSError, ConnectionError, TimeoutError)


def with_retry(fn: Callable[[], Any], max_retries: int = 5) -> Any:
    """Call fn() with exponential backoff on transient errors.

    Retries on HTTP 429 (rate limit), 500, 503, and transient network errors
    (OSError, ConnectionError, TimeoutError). Raises immediately on all
    other HTTP errors (e.g. 401, 403, 404).
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except HttpError as e:
            if e.resp.status in (429, 500, 503) and attempt < max_retries - 1:
                wait = 2**attempt
                logger.warning("API error %s, retrying in %ss...", e.resp.status, wait)
                time.sleep(wait)
            else:
                raise
        except _TRANSIENT_NETWORK_ERRORS as exc:
            if attempt < max_retries - 1:
                wait = 2**attempt
                logger.warning("Network error %s, retrying in %ss...", type(exc).__name__, wait)
                time.sleep(wait)
            else:
                raise
