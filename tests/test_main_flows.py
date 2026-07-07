"""Integration-style tests for main() entry points."""

from unittest.mock import MagicMock, patch


def _make_service():
    svc = MagicMock()
    svc.users().labels().list().execute.return_value = {
        'labels': [
            {'id': 'r', 'name': 'Job Rejections'},
            {'id': 'a', 'name': 'Job Applications Applied'},
        ]
    }
    svc.users().threads().list().execute.return_value = {'threads': []}
    return svc


def test_gmail_labeler_main_dry_run():
    from gmail_labeler import main
    svc = _make_service()
    with patch('gmail_labeler.get_gmail_service', return_value=svc), \
         patch('gmail_labeler.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('sys.argv', ['gmail_labeler.py', '--dry-run']), \
         patch('time.sleep'):
        main()


def test_gmail_labeler_main_no_args():
    from gmail_labeler import main
    svc = _make_service()
    svc.new_batch_http_request.return_value = MagicMock()
    with patch('gmail_labeler.get_gmail_service', return_value=svc), \
         patch('gmail_labeler.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('sys.argv', ['gmail_labeler.py']), \
         patch('time.sleep'):
        main()


def test_label_interviews_main_dry_run():
    from label_interviews import main
    svc = MagicMock()
    svc.users().labels().list().execute.return_value = {
        'labels': [{'id': 'label_int', 'name': 'Job Interviews'}]
    }
    svc.users().threads().list().execute.return_value = {'threads': []}
    with patch('label_interviews.get_gmail_service', return_value=svc), \
         patch('label_interviews.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('sys.argv', ['label_interviews.py', '--dry-run']), \
         patch('time.sleep'):
        main()


def test_label_interviews_main_no_args():
    from label_interviews import main
    svc = MagicMock()
    svc.users().labels().list().execute.return_value = {
        'labels': [{'id': 'label_int', 'name': 'Job Interviews'}]
    }
    svc.users().threads().list().execute.return_value = {'threads': []}
    svc.new_batch_http_request.return_value = MagicMock()
    with patch('label_interviews.get_gmail_service', return_value=svc), \
         patch('label_interviews.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('sys.argv', ['label_interviews.py']), \
         patch('time.sleep'):
        main()


def test_gmail_labeler_main_debug_log_level():
    from gmail_labeler import main
    svc = _make_service()
    with patch('gmail_labeler.get_gmail_service', return_value=svc), \
         patch('gmail_labeler.with_retry', side_effect=lambda fn, **kw: fn()), \
         patch('sys.argv', ['gmail_labeler.py', '--dry-run', '--log-level', 'DEBUG']), \
         patch('time.sleep'):
        main()
