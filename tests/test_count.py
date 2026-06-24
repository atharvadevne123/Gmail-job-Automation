"""Tests for count_emails module."""
import io
from unittest.mock import MagicMock, patch

import pytest

from count_emails import count_all, count_label, export_csv


@pytest.fixture()
def svc():
    return MagicMock()


def test_count_label_found(svc):
    svc.users().labels().list().execute.return_value = {
        "labels": [{"id": "Label_1", "name": "Job Rejections"}]
    }
    svc.users().labels().get().execute.return_value = {"threadsTotal": 42}
    assert count_label(svc, "Job Rejections") == 42


def test_count_label_not_found_returns_zero(svc):
    svc.users().labels().list().execute.return_value = {"labels": []}
    assert count_label(svc, "Missing Label") == 0


def test_count_label_zero_threads(svc):
    svc.users().labels().list().execute.return_value = {
        "labels": [{"id": "Label_2", "name": "Empty"}]
    }
    svc.users().labels().get().execute.return_value = {"threadsTotal": 0}
    assert count_label(svc, "Empty") == 0


def test_count_label_uses_threads_total_key(svc):
    svc.users().labels().list().execute.return_value = {
        "labels": [{"id": "L3", "name": "Test"}]
    }
    svc.users().labels().get().execute.return_value = {"threadsTotal": 7, "messagesTotal": 14}
    assert count_label(svc, "Test") == 7


def test_count_label_missing_key_returns_zero(svc):
    svc.users().labels().list().execute.return_value = {
        "labels": [{"id": "L4", "name": "NoKey"}]
    }
    svc.users().labels().get().execute.return_value = {}
    assert count_label(svc, "NoKey") == 0


def test_count_all_returns_dict(svc):
    with patch("count_emails.count_label", side_effect=lambda s, n: {"A": 10, "B": 5}.get(n, 0)):
        assert count_all(svc, ["A", "B"]) == {"A": 10, "B": 5}


def test_count_all_empty_labels(svc):
    assert count_all(svc, []) == {}


@pytest.mark.parametrize("name,expected", [
    ("Job Rejections", 3),
    ("Job Applications Applied", 7),
])
def test_count_all_parametrize(svc, name, expected):
    with patch("count_emails.count_label", side_effect=lambda s, n: expected if n == name else 0):
        assert count_all(svc, [name])[name] == expected


def test_export_csv_header_and_rows():
    buf = io.StringIO()
    export_csv({"Job Rejections": 5, "Job Applications Applied": 12}, output=buf)
    lines = buf.getvalue().strip().splitlines()
    assert lines[0] == "label,threads"
    assert "Job Rejections" in lines[1]
    assert "5" in lines[1]


def test_export_csv_empty():
    buf = io.StringIO()
    export_csv({}, output=buf)
    assert buf.getvalue().strip() == "label,threads"
