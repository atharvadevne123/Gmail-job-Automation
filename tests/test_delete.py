"""Tests for delete_job_emails module."""
from unittest.mock import MagicMock, patch

import pytest

from delete_job_emails import LABELS_TO_TRASH, get_label_id, trash_all_in_label


def test_labels_to_trash_nonempty():
    assert len(LABELS_TO_TRASH) > 0


def test_labels_to_trash_contains_rejections():
    assert "Job Rejections" in LABELS_TO_TRASH


def test_labels_to_trash_contains_applications():
    assert "Job Applications Applied" in LABELS_TO_TRASH


def test_get_label_id_found(mock_service):
    with patch("delete_job_emails.with_retry") as mock_retry:
        mock_retry.return_value = {
            "labels": [
                {"name": "Job Rejections", "id": "label_xyz"},
                {"name": "Other", "id": "other_id"},
            ]
        }
        assert get_label_id(mock_service, "Job Rejections") == "label_xyz"


def test_get_label_id_not_found(mock_service):
    with patch("delete_job_emails.with_retry") as mock_retry:
        mock_retry.return_value = {"labels": [{"name": "Other", "id": "other_id"}]}
        assert get_label_id(mock_service, "Nonexistent") is None


def test_trash_all_no_threads_returns_zero(mock_service):
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": []
    }
    with patch("delete_job_emails.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert trash_all_in_label(mock_service, "Job Rejections", "label123") == 0


def test_trash_all_trashes_threads_returns_count(mock_service):
    threads = [{"id": f"t{i}"} for i in range(4)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": threads
    }
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("delete_job_emails.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert trash_all_in_label(mock_service, "Job Rejections", "label123") == 4


def test_trash_all_deletes_label(mock_service):
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": []
    }
    with patch("delete_job_emails.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        trash_all_in_label(mock_service, "Job Rejections", "label123")
    mock_service.users.return_value.labels.return_value.delete.assert_called_with(
        userId="me", id="label123"
    )


def test_trash_all_dry_run_no_actual_trash(mock_service):
    threads = [{"id": f"t{i}"} for i in range(3)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": threads
    }
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("delete_job_emails.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert trash_all_in_label(mock_service, "Job Rejections", "label123", dry_run=True) == 3
    batch.execute.assert_not_called()
    mock_service.users.return_value.labels.return_value.delete.assert_not_called()


def test_trash_all_pagination(mock_service):
    page1 = [{"id": f"t{i}"} for i in range(5)]
    page2 = [{"id": f"t{i}"} for i in range(5, 8)]
    ex = mock_service.users.return_value.threads.return_value.list.return_value.execute
    ex.side_effect = [
        {"threads": page1, "nextPageToken": "tok2"},
        {"threads": page2},
    ]
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("delete_job_emails.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert trash_all_in_label(mock_service, "Job Rejections", "label123") == 8


@pytest.mark.parametrize("count", [0, 1, 10, 250])
def test_trash_all_returns_exact_count(mock_service, count):
    threads = [{"id": f"t{i}"} for i in range(count)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        "threads": threads
    }
    batch = MagicMock()
    mock_service.new_batch_http_request.return_value = batch
    with patch("delete_job_emails.with_retry", side_effect=lambda fn, **kw: fn()),          patch("time.sleep"):
        assert trash_all_in_label(mock_service, "Job Rejections", "label123") == count
