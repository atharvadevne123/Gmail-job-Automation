"""Gmail OAuth2 authentication and resilient API call utilities."""

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

logger = logging.getLogger(__name__)

__all__ = ["get_gmail_service", "with_retry"]

SCOPES: list[str] = ['https://www.googleapis.com/auth/gmail.modify']

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH: str = os.environ.get('GMAIL_TOKEN_PATH', os.path.join(BASE_DIR, 'token.pickle'))
CREDENTIALS_PATH: str = os.environ.get(
    'GMAIL_CREDENTIALS_PATH', os.path.join(BASE_DIR, 'credentials.json')
)


def get_gmail_service() -> Any:
    """Authenticate and return an authorized Gmail API service object.

    Loads cached credentials from TOKEN_PATH if available. Refreshes
    the token automatically when expired; falls back to a browser-based
    OAuth2 flow using the client secrets at CREDENTIALS_PATH.

    Returns:
        A ``googleapiclient.discovery.Resource`` for the Gmail v1 API.

    Raises:
        FileNotFoundError: If no cached token exists and credentials.json
            is not found at CREDENTIALS_PATH.
    """
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as f:
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

        with open(TOKEN_PATH, 'wb') as f:
            pickle.dump(creds, f)

    return build('gmail', 'v1', credentials=creds)


_TRANSIENT_NETWORK_ERRORS = (OSError, ConnectionError, TimeoutError)


def with_retry(fn: Callable[[], Any], max_retries: int = 5) -> Any:
    """Call ``fn()`` with exponential backoff on transient errors.

    Retries on HTTP 429, 500, 503 responses and on transient network
    exceptions (``OSError``, ``ConnectionError``, ``TimeoutError``).
    Non-retryable ``HttpError`` codes are re-raised immediately.

    Args:
        fn: Zero-argument callable to invoke.
        max_retries: Maximum number of attempts before re-raising the
            last exception. Defaults to 5.

    Returns:
        Whatever ``fn()`` returns on success.

    Raises:
        HttpError: On non-retryable HTTP errors, or after exhausting retries.
        OSError | ConnectionError | TimeoutError: After exhausting retries on
            network failures.
    """
    for attempt in range(max_retries):
        try:
            return fn()
        except HttpError as e:
            if e.resp.status in (429, 500, 503) and attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning("API error %s, retrying in %ss...", e.resp.status, wait)
                time.sleep(wait)
            else:
                raise
        except _TRANSIENT_NETWORK_ERRORS as e:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning("Network error %s, retrying in %ss...", type(e).__name__, wait)
                time.sleep(wait)
            else:
                raise
