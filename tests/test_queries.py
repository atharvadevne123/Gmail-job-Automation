"""Integrity tests for the keyword query lists used by the labelers."""

import pytest

from delete_job_emails import LABELS_TO_TRASH
from gmail_labeler import LABELS
from label_interviews import INTERVIEW_QUERIES


def _all_query_lists():
    return list(LABELS.values()) + [INTERVIEW_QUERIES]


@pytest.mark.parametrize("queries", _all_query_lists())
def test_queries_are_nonempty_strings(queries):
    assert queries, "query list must not be empty"
    for q in queries:
        assert isinstance(q, str)
        assert q.strip(), "query must not be blank"


@pytest.mark.parametrize("queries", _all_query_lists())
def test_queries_have_no_duplicates(queries):
    assert len(queries) == len(set(queries))


@pytest.mark.parametrize("queries", _all_query_lists())
def test_quoted_phrases_are_balanced(queries):
    for q in queries:
        assert q.count('"') % 2 == 0, f"unbalanced quotes in {q!r}"


def test_labels_to_trash_matches_labeler_labels():
    """Every label the delete script trashes must be one the labeler creates."""
    assert set(LABELS_TO_TRASH) <= set(LABELS.keys())


def test_interview_label_not_in_trash_list():
    """Interview invitations must never be auto-trashed."""
    assert "Job Interviews" not in LABELS_TO_TRASH
