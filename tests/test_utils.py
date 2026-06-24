"""Tests for utils module."""
import time
from unittest.mock import MagicMock, patch

import pytest

from utils import build_query, chunked, format_count, retry, sanitize_query


def test_build_query_single():
    assert build_query(["hello"]) == "hello"


def test_build_query_multiple():
    assert build_query(["a", "b", "c"]) == "a OR b OR c"


def test_build_query_and_operator():
    assert build_query(["x", "y"], operator="AND") == "x AND y"


def test_build_query_empty_returns_empty():
    assert build_query([]) == ""


def test_build_query_wraps_spaced_terms():
    assert build_query(["hello world"]) == "(hello world)"


def test_build_query_mixed_spacing():
    assert build_query(["foo", "bar baz"]) == "foo OR (bar baz)"


def test_chunked_even_split():
    assert list(chunked([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]


def test_chunked_uneven_split():
    assert list(chunked([1, 2, 3], 2)) == [[1, 2], [3]]


def test_chunked_size_larger_than_list():
    assert list(chunked([1], 5)) == [[1]]


def test_chunked_empty_list():
    assert list(chunked([], 3)) == []


def test_chunked_size_one():
    assert list(chunked([1, 2, 3], 1)) == [[1], [2], [3]]


def test_format_count_singular():
    assert format_count(1, "thread") == "1 thread"


def test_format_count_plural_auto():
    assert format_count(2, "thread") == "2 threads"


def test_format_count_custom_plural():
    assert format_count(3, "ox", "oxen") == "3 oxen"


def test_format_count_zero_uses_plural():
    assert format_count(0, "thread") == "0 threads"


@pytest.mark.parametrize("n,expected", [
    (1, "1 email"),
    (5, "5 emails"),
    (100, "100 emails"),
])
def test_format_count_parametrize(n, expected):
    assert format_count(n, "email") == expected


def test_sanitize_query_trims_whitespace():
    assert sanitize_query("  hello  ") == "hello"


def test_sanitize_query_collapses_spaces():
    assert sanitize_query("a  b   c") == "a b c"


def test_sanitize_query_no_change_on_clean():
    assert sanitize_query("a OR b") == "a OR b"


def test_retry_succeeds_on_first_attempt():
    fn = MagicMock(return_value=42)

    @retry(max_retries=3, delay=0.0)
    def decorated():
        return fn()

    assert decorated() == 42
    fn.assert_called_once()


def test_retry_retries_on_exception():
    fn = MagicMock(side_effect=[ValueError("err"), 99])

    @retry(max_retries=3, delay=0.0, exceptions=(ValueError,))
    def decorated():
        return fn()

    assert decorated() == 99
    assert fn.call_count == 2


def test_retry_raises_after_max():
    fn = MagicMock(side_effect=ValueError("always"))

    @retry(max_retries=2, delay=0.0, exceptions=(ValueError,))
    def decorated():
        return fn()

    with pytest.raises(ValueError):
        decorated()
    assert fn.call_count == 2


def test_retry_does_not_catch_unlisted_exception():
    fn = MagicMock(side_effect=TypeError("type error"))

    @retry(max_retries=3, delay=0.0, exceptions=(ValueError,))
    def decorated():
        return fn()

    with pytest.raises(TypeError):
        decorated()
    fn.assert_called_once()
