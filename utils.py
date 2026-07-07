"""Shared utility helpers for Gmail Job Automation scripts."""


def format_count(n: int, singular: str = "email", plural: str = "emails") -> str:
    """Return a human-readable count string.

    Args:
        n: The numeric count.
        singular: Word to use when ``n == 1``.
        plural: Word to use when ``n != 1``.

    Returns:
        A string like ``"1 email"`` or ``"42 emails"``.

    Examples:
        >>> format_count(1)
        '1 email'
        >>> format_count(0)
        '0 emails'
        >>> format_count(5)
        '5 emails'
    """
    word = singular if n == 1 else plural
    return f"{n} {word}"


def plural_s(n: int) -> str:
    """Return ``'s'`` when *n* is not 1, otherwise ``''``.

    Args:
        n: The count to check.

    Returns:
        ``''`` if n == 1, else ``'s'``.
    """
    return "" if n == 1 else "s"
