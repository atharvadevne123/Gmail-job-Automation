"""Shared pytest fixtures for Gmail job automation tests."""
import sys
from unittest.mock import MagicMock

import pytest

# Stub heavy C-extension Google libraries so tests run without them.
_google_stubs = [
    "google",
    "google.auth",
    "google.auth.transport",
    "google.auth.transport.requests",
    "google.auth.exceptions",
    "google.oauth2",
    "google_auth_oauthlib",
    "google_auth_oauthlib.flow",
    "googleapiclient",
    "googleapiclient.discovery",
    "googleapiclient.errors",
]
for _mod in _google_stubs:
    sys.modules.setdefault(_mod, MagicMock())


class _HttpError(Exception):
    def __init__(self, resp, content=b""):
        self.resp = resp
        self.content = content
        super().__init__(str(resp.status))


sys.modules["googleapiclient.errors"].HttpError = _HttpError


def make_http_error(status: int) -> _HttpError:
    """Factory helper for creating HttpError instances in tests."""
    resp = MagicMock()
    resp.status = status
    return _HttpError(resp=resp, content=b"error")


@pytest.fixture
def http_error():
    """Return the make_http_error factory."""
    return make_http_error


@pytest.fixture
def mock_service():
    """Fully mocked Gmail API service object."""
    service = MagicMock()

    service.users().labels().list().execute.return_value = {
        "labels": [
            {"id": "label_rej", "name": "Job Rejections"},
            {"id": "label_app", "name": "Job Applications Applied"},
            {"id": "label_int", "name": "Job Interviews"},
        ]
    }
    service.users().labels().create().execute.return_value = {
        "id": "label_new",
        "name": "New Label",
    }
    service.users().threads().list().execute.return_value = {"threads": []}
    service.users().threads().modify().execute.return_value = {}
    service.users().threads().trash().execute.return_value = {}
    service.users().labels().delete().execute.return_value = {}
    service.new_batch_http_request.return_value = MagicMock()

    return service


@pytest.fixture
def multi_page_threads():
    """Return two pages of thread IDs for pagination tests."""
    page1 = [{"id": f"t{i}"} for i in range(5)]
    page2 = [{"id": f"t{i}"} for i in range(5, 8)]
    return page1, page2


@pytest.fixture
def batch_with_errors(mock_service):
    """Batch mock that reports one error per execute call."""
    from unittest.mock import call

    batch = MagicMock()

    def execute_with_error():
        cb = mock_service.new_batch_http_request.call_args[1].get("callback")
        if cb:
            cb("req_0", None, Exception("batch error"))

    batch.execute.side_effect = execute_with_error
    mock_service.new_batch_http_request.return_value = batch
    return mock_service
