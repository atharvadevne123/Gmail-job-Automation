import pytest
from unittest.mock import MagicMock, patch
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
