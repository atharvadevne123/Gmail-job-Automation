"""Tests for scripts/run_all.py."""

from unittest.mock import MagicMock, patch

import pytest


def test_run_all_dry_run_returns_dict():
    from scripts.run_all import run_all

    mock_service = MagicMock()
    mock_service.users().labels().list().execute.return_value = {'labels': []}
    mock_service.users().threads().list().execute.return_value = {'threads': []}

    with patch('scripts.run_all.get_gmail_service', return_value=mock_service), \
         patch('scripts.run_all.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('scripts.run_all.label_threads', return_value=0), \
         patch('scripts.run_all.label_interview_threads', return_value=0), \
         patch('scripts.run_all.get_or_create_label', return_value='dry_id'), \
         patch('scripts.run_all.get_or_create_interview_label', return_value='dry_id2'), \
         patch('time.sleep'):
        result = run_all(dry_run=True)

    assert isinstance(result, dict)


def test_run_all_live_returns_dict():
    from scripts.run_all import run_all

    mock_service = MagicMock()
    mock_service.users().labels().list().execute.return_value = {'labels': []}
    mock_service.users().threads().list().execute.return_value = {'threads': []}

    with patch('scripts.run_all.get_gmail_service', return_value=mock_service), \
         patch('scripts.run_all.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('scripts.run_all.label_threads', return_value=5), \
         patch('scripts.run_all.label_interview_threads', return_value=3), \
         patch('scripts.run_all.get_or_create_label', return_value='label_id'), \
         patch('scripts.run_all.get_or_create_interview_label', return_value='int_id'), \
         patch('time.sleep'):
        result = run_all(dry_run=False)

    assert isinstance(result, dict)
    assert sum(result.values()) > 0


def test_run_all_result_contains_all_labels():
    from gmail_labeler import LABELS
    from label_interviews import LABEL_NAME as INTERVIEW_LABEL
    from scripts.run_all import run_all

    mock_service = MagicMock()
    mock_service.users().labels().list().execute.return_value = {'labels': []}

    with patch('scripts.run_all.get_gmail_service', return_value=mock_service), \
         patch('scripts.run_all.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('scripts.run_all.label_threads', return_value=0), \
         patch('scripts.run_all.label_interview_threads', return_value=0), \
         patch('scripts.run_all.get_or_create_label', return_value='id'), \
         patch('scripts.run_all.get_or_create_interview_label', return_value='id2'):
        result = run_all(dry_run=True)

    for label in list(LABELS.keys()) + [INTERVIEW_LABEL]:
        assert label in result
