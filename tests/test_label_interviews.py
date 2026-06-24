"""Tests for label_interviews module."""
from unittest.mock import MagicMock, patch

import pytest

from label_interviews import INTERVIEW_QUERIES, get_or_create_label, label_interview_threads


class TestGetOrCreateLabel:
    def test_returns_existing_label_id(self, mock_service):
        mock_service.users().labels().list().execute.return_value = {
            "labels": [{"id": "label_int", "name": "Job Interviews"}]
        }
        assert get_or_create_label(mock_service, "Job Interviews") == "label_int"

    def test_creates_label_when_absent(self, mock_service):
        mock_service.users().labels().list().execute.return_value = {"labels": []}
        mock_service.users().labels().create().execute.return_value = {
            "id": "label_new",
            "name": "Job Interviews",
        }
        assert get_or_create_label(mock_service, "Job Interviews") == "label_new"

    def test_case_sensitive_name_match(self, mock_service):
        mock_service.users().labels().list().execute.return_value = {
            "labels": [{"id": "x", "name": "job interviews"}]
        }
        mock_service.users().labels().create().execute.return_value = {
            "id": "new_id",
            "name": "Job Interviews",
        }
        assert get_or_create_label(mock_service, "Job Interviews") == "new_id"


class TestLabelInterviewThreads:
    def test_returns_zero_for_no_threads(self, mock_service):
        mock_service.users().threads().list().execute.return_value = {"threads": []}
        assert label_interview_threads(mock_service, "label_int") == 0

    def test_labels_threads_and_returns_count(self, mock_service):
        threads = [{"id": f"t{i}"} for i in range(6)]
        mock_service.users().threads().list().execute.side_effect = [
            {"threads": threads},
            {"threads": []},
        ]
        batch = MagicMock()
        mock_service.new_batch_http_request.return_value = batch
        with patch("label_interviews.time.sleep"):
            assert label_interview_threads(mock_service, "label_int") == 6
        assert batch.execute.called

    def test_dry_run_returns_count_without_modifying(self, mock_service):
        threads = [{"id": f"t{i}"} for i in range(3)]
        mock_service.users().threads().list().execute.return_value = {
            "threads": threads
        }
        batch = MagicMock()
        mock_service.new_batch_http_request.return_value = batch
        with patch("label_interviews.time.sleep"):
            assert label_interview_threads(mock_service, "label_int", dry_run=True) == 3
        batch.execute.assert_not_called()

    def test_pagination_sums_all_pages(self, mock_service):
        page1 = [{"id": f"t{i}"} for i in range(4)]
        page2 = [{"id": f"t{i}"} for i in range(4, 7)]
        mock_service.users().threads().list().execute.side_effect = [
            {"threads": page1, "nextPageToken": "tok2"},
            {"threads": page2},
        ]
        batch = MagicMock()
        mock_service.new_batch_http_request.return_value = batch
        with patch("label_interviews.time.sleep"):
            assert label_interview_threads(mock_service, "label_int") == 7


class TestInterviewQueries:
    def test_has_minimum_query_count(self):
        assert len(INTERVIEW_QUERIES) >= 19

    def test_all_queries_are_strings(self):
        assert all(isinstance(q, str) for q in INTERVIEW_QUERIES)

    def test_queries_are_unique(self):
        assert len(INTERVIEW_QUERIES) == len(set(INTERVIEW_QUERIES))

    @pytest.mark.parametrize("keyword", [
        "interview",
        "phone screen",
        "coding challenge",
    ])
    def test_key_patterns_present(self, keyword):
        combined = " ".join(INTERVIEW_QUERIES)
        assert keyword in combined
