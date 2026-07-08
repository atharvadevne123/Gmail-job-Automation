"""Shared utilities for Gmail job automation."""
from __future__ import annotations

import logging
import re
import time
from collections.abc import Generator
from functools import wraps
from typing import Any, Callable, TypeVar

__all__ = [
    "build_query",
    "chunked",
    "format_count",
    "format_duration",
    "plural_s",
    "sanitize_query",
    "retry",
    "truncate",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())

_F = TypeVar("_F", bound=Callable[..., Any])


def build_query(terms: list[str], operator: str = "OR") -> str:
    """Join search terms with a boolean operator."""
    if not terms:
        return ""
    return f" {operator} ".join(f"({t})" if " " in t else t for t in terms)


def chunked(items: list, size: int) -> Generator[list, None, None]:
    """Yield successive chunks of a list."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


def format_count(n: int, singular: str = "email", plural: str | None = None) -> str:
    """Return a human-readable count string."""
    noun = singular if n == 1 else (plural or f"{singular}s")
    return f"{n} {noun}"


def format_duration(seconds: float) -> str:
    """Return a human-readable duration string from a number of seconds."""
    seconds = max(0.0, seconds)
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {secs:02d}s"
    hours, mins = divmod(minutes, 60)
    return f"{hours}h {mins:02d}m {secs:02d}s"


def plural_s(n: int) -> str:
    """Return ``'s'`` when *n* is not 1, otherwise ``''``."""
    return "" if n == 1 else "s"


def sanitize_query(query: str) -> str:
    """Remove duplicate whitespace and trim a Gmail search query."""
    return re.sub(r" {2,}", " ", query).strip()


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max_length, appending suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def retry(
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[_F], _F]:
    """Decorator: retry a function on specified exceptions with fixed delay."""

    def decorator(fn: _F) -> _F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: Exception | None = None
            for attempt in range(max_retries):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_retries - 1:
                        time.sleep(delay)
            raise last_exc  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator
