import pytest
from unittest.mock import MagicMock, patch

from gmail_labeler import get_or_create_label, label_threads


def test_get_or_create_label_finds_existing(mock_service):
    existing = [
        {'name': 'Job Rejections', 'id': 'label_abc'},
        {'name': 'Other', 'id': 'other_id'},
    ]
    label_id = get_or_create_label(mock_service, 'Job Rejections', existing)
    assert label_id == 'label_abc'
    mock_service.users.return_value.labels.return_value.create.assert_not_called()


def test_get_or_create_label_creates_new_when_missing(mock_service):
    existing = [{'name': 'Other', 'id': 'other_id'}]
    mock_service.users.return_value.labels.return_value.create.return_value.execute.return_value = {
        'id': 'new_label_id',
        'name': 'Job Applications Applied',
    }
    with patch('gmail_labeler.with_retry', side_effect=lambda fn, **kw: fn()):
        label_id = get_or_create_label(mock_service, 'Job Applications Applied', existing)
    assert label_id == 'new_label_id'


def test_label_threads_returns_zero_when_no_threads(mock_service):
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        'threads': []
    }
    with patch('gmail_labeler.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('time.sleep'):
        count = label_threads(mock_service, 'Job Rejections', 'label123', ['q1', 'q2'])
    assert count == 0


def test_label_threads_single_page(mock_service):
    threads = [{'id': 'tid1'}, {'id': 'tid2'}, {'id': 'tid3'}]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        'threads': threads
    }
    mock_batch = MagicMock()
    mock_service.new_batch_http_request.return_value = mock_batch

    with patch('gmail_labeler.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('time.sleep'):
        count = label_threads(mock_service, 'Job Rejections', 'label123', ['q1'])

    assert count == 3
    mock_batch.execute.assert_called_once()


def test_label_threads_pagination(mock_service):
    page1 = [{'id': f'tid{i}'} for i in range(5)]
    page2 = [{'id': f'tid{i}'} for i in range(5, 8)]
    execute_mock = (
        mock_service.users.return_value.threads.return_value.list.return_value.execute
    )
    execute_mock.side_effect = [
        {'threads': page1, 'nextPageToken': 'token_page2'},
        {'threads': page2},
    ]
    mock_batch = MagicMock()
    mock_service.new_batch_http_request.return_value = mock_batch

    with patch('gmail_labeler.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('time.sleep'):
        count = label_threads(mock_service, 'Job Rejections', 'label123', ['q1'])

    assert count == 8
    assert mock_batch.execute.call_count == 2
