"""Tests for utils module."""

import pytest

from utils import format_count, plural_s


class TestFormatCount:
    def test_singular(self):
        assert format_count(1) == "1 email"

    def test_plural(self):
        assert format_count(5) == "5 emails"

    def test_zero(self):
        assert format_count(0) == "0 emails"

    def test_custom_words(self):
        assert format_count(1, singular="thread", plural="threads") == "1 thread"
        assert format_count(3, singular="thread", plural="threads") == "3 threads"

    @pytest.mark.parametrize("n,expected", [
        (0, "0 emails"),
        (1, "1 email"),
        (2, "2 emails"),
        (100, "100 emails"),
        (-1, "-1 emails"),
    ])
    def test_parametrized(self, n, expected):
        assert format_count(n) == expected


class TestPluralS:
    def test_singular_returns_empty(self):
        assert plural_s(1) == ""

    def test_plural_returns_s(self):
        assert plural_s(2) == "s"

    def test_zero_returns_s(self):
        assert plural_s(0) == "s"

    @pytest.mark.parametrize("n,expected", [
        (0, "s"), (1, ""), (2, "s"), (10, "s"), (-1, "s")
    ])
    def test_parametrized(self, n, expected):
        assert plural_s(n) == expected
