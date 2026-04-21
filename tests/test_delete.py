import pytest
from unittest.mock import MagicMock, patch

from delete_job_emails import get_label_id, trash_all_in_label


def test_get_label_id_found(mock_service):
    with patch('delete_job_emails.with_retry') as mock_retry:
        mock_retry.return_value = {
            'labels': [
                {'name': 'Job Rejections', 'id': 'label_xyz'},
                {'name': 'Other', 'id': 'other_id'},
            ]
        }
        result = get_label_id(mock_service, 'Job Rejections')
    assert result == 'label_xyz'


def test_get_label_id_not_found(mock_service):
    with patch('delete_job_emails.with_retry') as mock_retry:
        mock_retry.return_value = {'labels': [{'name': 'Other', 'id': 'other_id'}]}
        result = get_label_id(mock_service, 'Nonexistent Label')
    assert result is None


def test_trash_all_no_threads_returns_zero(mock_service):
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        'threads': []
    }
    with patch('delete_job_emails.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('time.sleep'):
        count = trash_all_in_label(mock_service, 'Job Rejections', 'label123')
    assert count == 0


def test_trash_all_trashes_threads_and_returns_count(mock_service):
    threads = [{'id': f'tid{i}'} for i in range(4)]
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        'threads': threads
    }
    mock_batch = MagicMock()
    mock_service.new_batch_http_request.return_value = mock_batch

    with patch('delete_job_emails.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('time.sleep'):
        count = trash_all_in_label(mock_service, 'Job Rejections', 'label123')

    assert count == 4
    mock_batch.execute.assert_called_once()


def test_trash_all_deletes_label_after_trashing(mock_service):
    mock_service.users.return_value.threads.return_value.list.return_value.execute.return_value = {
        'threads': []
    }
    with patch('delete_job_emails.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('time.sleep'):
        trash_all_in_label(mock_service, 'Job Rejections', 'label123')

    mock_service.users.return_value.labels.return_value.delete.assert_called_once_with(
        userId='me', id='label123'
    )
