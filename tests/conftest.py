import sys
from unittest.mock import MagicMock

import pytest

# Stub out google-auth and google-api-python-client before any module import
# so tests run without the system cryptography C extension.
_google_stubs = [
    'google', 'google.auth', 'google.auth.transport', 'google.auth.transport.requests',
    'google.auth.exceptions', 'google.oauth2', 'google_auth_oauthlib',
    'google_auth_oauthlib.flow', 'googleapiclient', 'googleapiclient.discovery',
    'googleapiclient.errors',
]
for _mod in _google_stubs:
    sys.modules.setdefault(_mod, MagicMock())


class _HttpError(Exception):
    def __init__(self, resp, content=b''):
        self.resp = resp
        self.content = content
        super().__init__(str(resp.status))


sys.modules['googleapiclient.errors'].HttpError = _HttpError


@pytest.fixture
def mock_service():
    """Return a fully mocked Gmail API service object."""
    service = MagicMock()

    service.users().labels().list().execute.return_value = {
        'labels': [
            {'id': 'label_rej', 'name': 'Job Rejections'},
            {'id': 'label_app', 'name': 'Job Applications Applied'},
            {'id': 'label_int', 'name': 'Job Interviews'},
        ]
    }
    service.users().labels().create().execute.return_value = {
        'id': 'label_new', 'name': 'New Label'
    }
    service.users().threads().list().execute.return_value = {'threads': []}
    service.users().threads().modify().execute.return_value = {}
    service.users().threads().trash().execute.return_value = {}
    service.users().labels().delete().execute.return_value = {}
    service.new_batch_http_request.return_value = MagicMock()

    return service
