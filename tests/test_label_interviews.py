from unittest.mock import MagicMock, patch

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
