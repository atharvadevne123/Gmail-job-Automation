"""Shared utilities for Gmail job automation."""
from __future__ import annotations

import logging
import re
import time
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

__all__ = ["build_query", "chunked", "format_count", "sanitize_query", "retry"]

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


def format_count(n: int, singular: str, plural: str | None = None) -> str:
    """Return a human-readable count string."""
    noun = singular if n == 1 else (plural or f"{singular}s")
    return f"{n} {noun}"


def sanitize_query(query: str) -> str:
    """Remove duplicate whitespace and trim a Gmail search query."""
    return re.sub(r" {2,}", " ", query).strip()


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
