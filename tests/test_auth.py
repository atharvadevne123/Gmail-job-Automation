"""Tests for auth module."""
from unittest.mock import MagicMock, mock_open, patch

import pytest
from googleapiclient.errors import HttpError

from auth import SCOPES, is_authenticated, with_retry


def _err(status: int) -> HttpError:
    resp = MagicMock()
    resp.status = status
    return HttpError(resp=resp, content=b"error")


def test_scopes_contains_gmail_modify():
    assert any("gmail.modify" in s for s in SCOPES)


def test_with_retry_success():
    fn = MagicMock(return_value="result")
    assert with_retry(fn) == "result"
    fn.assert_called_once()


def test_with_retry_retries_on_429():
    fn = MagicMock(side_effect=[_err(429), "ok"])
    with patch("time.sleep"):
        assert with_retry(fn, max_retries=3) == "ok"
    assert fn.call_count == 2


def test_with_retry_retries_on_503():
    fn = MagicMock(side_effect=[_err(503), _err(503), "ok"])
    with patch("time.sleep"):
        assert with_retry(fn, max_retries=5) == "ok"
    assert fn.call_count == 3


def test_with_retry_retries_on_500():
    fn = MagicMock(side_effect=[_err(500), "done"])
    with patch("time.sleep"):
        assert with_retry(fn, max_retries=2) == "done"


def test_with_retry_raises_after_max():
    fn = MagicMock(side_effect=_err(429))
    with patch("time.sleep"), pytest.raises(HttpError):
        with_retry(fn, max_retries=3)
    assert fn.call_count == 3


def test_with_retry_raises_immediately_on_non_retryable():
    fn = MagicMock(side_effect=_err(404))
    with pytest.raises(HttpError):
        with_retry(fn, max_retries=3)
    fn.assert_called_once()


def test_with_retry_retries_on_connection_error():
    fn = MagicMock(side_effect=[ConnectionError("reset"), "ok"])
    with patch("time.sleep"):
        assert with_retry(fn, max_retries=3) == "ok"
    assert fn.call_count == 2


def test_with_retry_retries_on_timeout_error():
    fn = MagicMock(side_effect=[TimeoutError("timed out"), "ok"])
    with patch("time.sleep"):
        assert with_retry(fn, max_retries=3) == "ok"
    assert fn.call_count == 2


def test_with_retry_raises_network_error_after_max():
    fn = MagicMock(side_effect=OSError("network down"))
    with patch("time.sleep"), pytest.raises(OSError):
        with_retry(fn, max_retries=2)
    assert fn.call_count == 2


@pytest.mark.parametrize("status", [429, 500, 503])
def test_with_retry_retries_all_retryable_statuses(status):
    fn = MagicMock(side_effect=[_err(status), "ok"])
    with patch("time.sleep"):
        assert with_retry(fn, max_retries=3) == "ok"


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_with_retry_does_not_retry_non_retryable(status):
    fn = MagicMock(side_effect=_err(status))
    with pytest.raises(HttpError):
        with_retry(fn, max_retries=3)
    fn.assert_called_once()


def test_with_retry_max_retries_one_means_no_retry():
    fn = MagicMock(side_effect=_err(429))
    with pytest.raises(HttpError):
        with_retry(fn, max_retries=1)
    fn.assert_called_once()


def test_get_gmail_service_raises_when_credentials_missing(tmp_path):
    from auth import get_gmail_service
    with patch("auth.TOKEN_PATH", str(tmp_path / "token.pickle")),          patch("auth.CREDENTIALS_PATH", str(tmp_path / "credentials.json")):
        with pytest.raises(FileNotFoundError, match="credentials.json not found"):
            get_gmail_service()


def test_get_gmail_service_loads_valid_token(tmp_path):
    from auth import get_gmail_service
    creds = MagicMock()
    creds.valid = True
    with patch("auth.TOKEN_PATH", str(tmp_path / "token.pickle")),          patch("auth.os.path.exists", return_value=True),          patch("builtins.open", mock_open()),          patch("auth.pickle.load", return_value=creds),          patch("auth.build") as mock_build:
        mock_build.return_value = MagicMock()
        get_gmail_service()
        assert mock_build.called


def test_is_authenticated_false_when_no_token(tmp_path):
    with patch("auth.TOKEN_PATH", str(tmp_path / "token.pickle")):
        assert is_authenticated() is False


def test_is_authenticated_true_when_valid_token(tmp_path):
    creds = MagicMock()
    creds.valid = True
    with patch("auth.os.path.exists", return_value=True), \
         patch("builtins.open", mock_open()), \
         patch("auth.pickle.load", return_value=creds):
        assert is_authenticated() is True


def test_is_authenticated_false_when_token_invalid(tmp_path):
    creds = MagicMock()
    creds.valid = False
    with patch("auth.os.path.exists", return_value=True), \
         patch("builtins.open", mock_open()), \
         patch("auth.pickle.load", return_value=creds):
        assert is_authenticated() is False
