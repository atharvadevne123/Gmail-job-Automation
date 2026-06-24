"""Tests for count_emails module."""
from unittest.mock import MagicMock

import pytest

from count_emails import count_label


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
