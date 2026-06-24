"""Shared utilities for Gmail job automation."""
from __future__ import annotations

import logging
from typing import Generator

__all__ = ["build_query", "chunked", "format_count"]

logging.getLogger(__name__).addHandler(logging.NullHandler())


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
