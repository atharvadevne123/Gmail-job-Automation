"""Tests for gmail_labeler module."""
from unittest.mock import MagicMock, patch

import pytest

from gmail_labeler import (
    APPLICATION_LABEL,
    LABELS,
    REJECTION_LABEL,
    get_or_create_label,
    label_threads,
)


def test_rejection_label_constant():
    assert REJECTION_LABEL == "Job Rejections"


def test_application_label_constant():
    assert APPLICATION_LABEL == "Job Applications Applied"


def test_labels_dict_has_both_keys():
    assert REJECTION_LABEL in LABELS
    assert APPLICATION_LABEL in LABELS


def test_labels_rejection_queries_nonempty():
    assert len(LABELS[REJECTION_LABEL]) > 0


def test_labels_application_queries_nonempty():
    assert len(LABELS[APPLICATION_LABEL]) > 0


def test_get_or_create_label_finds_existing(mock_service):
    existing = [{"name": "Job Rejections", "id": "label_abc"}]
    mock_service.users.return_value.labels.return_value.create.reset_mock()
    assert get_or_create_label(mock_service, "Job Rejections", existing) == "label_abc"
    mock_service.users.return_value.labels.return_value.create.assert_not_called()


def test_get_or_create_label_creates_when_missing(mock_service):
    existing = [{"name": "Other", "id": "other_id"}]
    mock_service.users.return_value.labels.return_value.create.return_value.execute.return_value = {
        "id": "new_label_id",
        "name": "Job Applications Applied",
    }
    with patch("gmail_labeler.with_retry", side_effect=lambda fn, **kw: fn()):
        assert (
            get_or_create_label(mock_service, "Job Applications Applied", existing)
            == "new_label_id"
        )


def test_label_threads_returns_zero_for_no_threads(mock_service):
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": []
    }
    with patch("gmail_labeler.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert label_threads(mock_service, "Job Rejections", "label123", ["q1"]) == 0


def test_label_threads_single_page(mock_service):
    threads = [{"id": f"t{i}"} for i in range(3)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": threads
    }
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("gmail_labeler.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert label_threads(mock_service, "Job Rejections", "label123", ["q1"]) == 3


def test_label_threads_pagination(mock_service):
    page1 = [{"id": f"t{i}"} for i in range(5)]
    page2 = [{"id": f"t{i}"} for i in range(5, 8)]
    ex = mock_service.users.return_value.threads.return_value.list.return_value.execute
    ex.side_effect = [
        {"threads": page1, "nextPageToken": "tok2"},
        {"threads": page2},
    ]
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("gmail_labeler.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert label_threads(mock_service, "Job Rejections", "label123", ["q1"]) == 8


def test_dry_run_does_not_create_label(mock_service):
    create = mock_service.users.return_value.labels.return_value.create
    create.reset_mock()
    result = get_or_create_label(mock_service, "Job Rejections", [], dry_run=True)
    assert result.startswith("dry_run_")
    create.assert_not_called()


def test_dry_run_counts_without_modifying(mock_service):
    threads = [{"id": f"t{i}"} for i in range(4)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": threads
    }
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("gmail_labeler.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        count = label_threads(
            mock_service, "Job Rejections", "label123", ["q"], dry_run=True
        )
    assert count == 4
    batch.execute.assert_not_called()


@pytest.mark.parametrize("thread_count", [1, 50, 100, 101, 200])
def test_label_threads_various_counts(mock_service, thread_count):
    threads = [{"id": f"t{i}"} for i in range(thread_count)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": threads
    }
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("gmail_labeler.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert label_threads(mock_service, "Job Rejections", "label123", ["q"]) == thread_count


def test_label_threads_custom_batch_size(mock_service):
    threads = [{"id": f"t{i}"} for i in range(6)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": threads
    }
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("gmail_labeler.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        count = label_threads(
            mock_service, "Job Rejections", "label123", ["q"], batch_size=2
        )
    assert count == 6
    assert batch.execute.call_count == 3
