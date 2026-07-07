from unittest.mock import MagicMock, patch

import pytest

from label_interviews import get_or_create_label, label_interview_threads


class TestGetOrCreateLabel:
    def test_returns_existing_label_id(self, mock_service):
        mock_service.users().labels().list().execute.return_value = {
            'labels': [{'id': 'label_int', 'name': 'Job Interviews'}]
        }
        result = get_or_create_label(mock_service, 'Job Interviews')
        assert result == 'label_int'

    def test_creates_label_when_absent(self, mock_service):
        mock_service.users().labels().list().execute.return_value = {'labels': []}
        mock_service.users().labels().create().execute.return_value = {
            'id': 'label_new', 'name': 'Job Interviews'
        }
        result = get_or_create_label(mock_service, 'Job Interviews')
        assert result == 'label_new'

    def test_dry_run_does_not_create_label(self, mock_service):
        mock_service.users().labels().list().execute.return_value = {'labels': []}
        label_id = get_or_create_label(mock_service, 'Job Interviews', dry_run=True)
        assert label_id.startswith('dry_run_')

    def test_dry_run_returns_placeholder_id(self, mock_service):
        mock_service.users().labels().list().execute.return_value = {'labels': []}
        label_id = get_or_create_label(mock_service, 'Job Interviews', dry_run=True)
        assert label_id == 'dry_run_Job Interviews'

    @pytest.mark.parametrize("label_name", [
        "Job Interviews",
        "Job Rejections",
        "Job Applications Applied",
    ])
    def test_returns_correct_id_for_various_labels(self, mock_service, label_name):
        mock_service.users().labels().list().execute.return_value = {
            'labels': [{'id': f'id_{label_name}', 'name': label_name}]
        }
        result = get_or_create_label(mock_service, label_name)
        assert result == f'id_{label_name}'


class TestLabelInterviewThreads:
    def test_returns_zero_when_no_threads(self, mock_service):
        mock_service.users().threads().list().execute.return_value = {'threads': []}
        count = label_interview_threads(mock_service, 'label_int')
        assert count == 0

    def test_labels_threads_and_returns_count(self, mock_service):
        threads = [{'id': f'thread_{i}'} for i in range(6)]
        mock_service.users().threads().list().execute.side_effect = [
            {'threads': threads, 'nextPageToken': None},
            {'threads': []},
        ]
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        with patch('label_interviews.time.sleep'):
            count = label_interview_threads(mock_service, 'label_int')

        assert count == 6
        assert batch_mock.execute.called

    def test_dry_run_counts_without_modifying(self, mock_service):
        threads = [{'id': f't{i}'} for i in range(5)]
        mock_service.users().threads().list().execute.return_value = {'threads': threads}
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        with patch('label_interviews.time.sleep'):
            count = label_interview_threads(mock_service, 'dry_run_label', dry_run=True)

        assert count == 5
        batch_mock.execute.assert_not_called()

    def test_dry_run_pagination(self, mock_service):
        page1 = [{'id': f't{i}'} for i in range(3)]
        page2 = [{'id': f't{i}'} for i in range(3, 6)]
        mock_service.users().threads().list().execute.side_effect = [
            {'threads': page1, 'nextPageToken': 'tok2'},
            {'threads': page2},
        ]
        with patch('label_interviews.time.sleep'):
            count = label_interview_threads(mock_service, 'dry_run_label', dry_run=True)
        assert count == 6

    def test_pagination_across_pages(self, mock_service):
        page1 = [{'id': f'tid{i}'} for i in range(5)]
        page2 = [{'id': f'tid{i}'} for i in range(5, 8)]
        mock_service.users().threads().list().execute.side_effect = [
            {'threads': page1, 'nextPageToken': 'token2'},
            {'threads': page2},
        ]
        batch_mock = MagicMock()
        mock_service.new_batch_http_request.return_value = batch_mock

        with patch('label_interviews.time.sleep'):
            count = label_interview_threads(mock_service, 'label_int')

        assert count == 8
        assert batch_mock.execute.call_count == 2
