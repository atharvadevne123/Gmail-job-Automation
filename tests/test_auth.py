from unittest.mock import MagicMock, mock_open, patch

import pytest
from googleapiclient.errors import HttpError

from auth import with_retry


def _http_error(status: int) -> HttpError:
    resp = MagicMock()
    resp.status = status
    return HttpError(resp=resp, content=b"error")


def test_with_retry_success():
    fn = MagicMock(return_value="result")
    assert with_retry(fn) == "result"
    fn.assert_called_once()


def test_with_retry_retries_on_429():
    err = _http_error(429)
    fn = MagicMock(side_effect=[err, "ok"])
    with patch("time.sleep"):
        result = with_retry(fn, max_retries=3)
    assert result == "ok"
    assert fn.call_count == 2


def test_with_retry_retries_on_503():
    err = _http_error(503)
    fn = MagicMock(side_effect=[err, err, "ok"])
    with patch("time.sleep"):
        result = with_retry(fn, max_retries=5)
    assert result == "ok"
    assert fn.call_count == 3


def test_with_retry_raises_after_max_retries():
    err = _http_error(429)
    fn = MagicMock(side_effect=err)
    with patch("time.sleep"), pytest.raises(HttpError):
        with_retry(fn, max_retries=3)
    assert fn.call_count == 3


def test_with_retry_raises_immediately_on_non_retryable_error():
    err = _http_error(404)
    fn = MagicMock(side_effect=err)
    with pytest.raises(HttpError):
        with_retry(fn, max_retries=3)
    fn.assert_called_once()


def test_with_retry_retries_on_500():
    err = _http_error(500)
    fn = MagicMock(side_effect=[err, "done"])
    with patch("time.sleep"):
        result = with_retry(fn, max_retries=2)
    assert result == "done"


def test_with_retry_retries_on_connection_error():
    fn = MagicMock(side_effect=[ConnectionError("reset"), "ok"])
    with patch("time.sleep"):
        result = with_retry(fn, max_retries=3)
    assert result == "ok"
    assert fn.call_count == 2


def test_with_retry_retries_on_timeout_error():
    fn = MagicMock(side_effect=[TimeoutError("timed out"), "ok"])
    with patch("time.sleep"):
        result = with_retry(fn, max_retries=3)
    assert result == "ok"
    assert fn.call_count == 2


def test_with_retry_raises_network_error_after_max_retries():
    fn = MagicMock(side_effect=OSError("network down"))
    with patch("time.sleep"), pytest.raises(OSError):
        with_retry(fn, max_retries=2)
    assert fn.call_count == 2


@pytest.mark.parametrize("status_code", [429, 500, 503])
def test_with_retry_retries_on_all_retryable_codes(status_code):
    err = _http_error(status_code)
    fn = MagicMock(side_effect=[err, "recovered"])
    with patch("time.sleep"):
        result = with_retry(fn, max_retries=3)
    assert result == "recovered"
    assert fn.call_count == 2


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 422])
def test_with_retry_raises_immediately_on_non_retryable_codes(status_code):
    err = _http_error(status_code)
    fn = MagicMock(side_effect=err)
    with pytest.raises(HttpError):
        with_retry(fn, max_retries=5)
    fn.assert_called_once()


@pytest.mark.parametrize("exc_type", [OSError, ConnectionError, TimeoutError])
def test_with_retry_handles_all_network_errors(exc_type):
    fn = MagicMock(side_effect=[exc_type("transient"), "ok"])
    with patch("time.sleep"):
        result = with_retry(fn, max_retries=3)
    assert result == "ok"
    assert fn.call_count == 2


def test_with_retry_uses_exponential_backoff():
    err = _http_error(429)
    fn = MagicMock(side_effect=[err, err, "ok"])
    sleep_calls = []
    with patch("time.sleep", side_effect=lambda s: sleep_calls.append(s)):
        with_retry(fn, max_retries=5)
    assert sleep_calls == [1, 2]


# --- get_gmail_service tests ---

def test_get_gmail_service_raises_when_credentials_missing(tmp_path):
    from auth import get_gmail_service
    with patch('auth.TOKEN_PATH', str(tmp_path / 'token.pickle')), \
         patch('auth.CREDENTIALS_PATH', str(tmp_path / 'credentials.json')):
        with pytest.raises(FileNotFoundError, match='credentials.json not found'):
            get_gmail_service()


def test_get_gmail_service_loads_valid_token(tmp_path):
    from auth import get_gmail_service
    creds = MagicMock()
    creds.valid = True

    with patch('auth.TOKEN_PATH', str(tmp_path / 'token.pickle')), \
         patch('auth.os.path.exists', return_value=True), \
         patch('builtins.open', mock_open()), \
         patch('auth.pickle.load', return_value=creds), \
         patch('auth.build') as mock_build:
        mock_build.return_value = MagicMock()
        get_gmail_service()
        assert mock_build.called


def test_get_gmail_service_refreshes_expired_token(tmp_path):
    from auth import get_gmail_service
    creds = MagicMock()
    creds.valid = False
    creds.expired = True
    creds.refresh_token = "tok"

    with patch('auth.TOKEN_PATH', str(tmp_path / 'token.pickle')), \
         patch('auth.os.path.exists', return_value=True), \
         patch('builtins.open', mock_open()), \
         patch('auth.pickle.load', return_value=creds), \
         patch('auth.pickle.dump'), \
         patch('auth.build') as mock_build:
        mock_build.return_value = MagicMock()
        get_gmail_service()
        creds.refresh.assert_called_once()
