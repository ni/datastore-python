"""Query results data type for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


class QueryResults(list[T]):
    """One page of query results with a continuation token when more results exist."""

    next_page_token: str
    """Opaque token for retrieving the next page, or an empty string when there is none."""

    def __init__(
        self,
        items: Iterable[T] = (),
        next_link: str = "",
        *,
        next_page_token: str | None = None,
    ) -> None:
        """Initialize a QueryResults instance.

        Args:
            items: The results on this page.
            next_link: Legacy name for the continuation token.
            next_page_token: Token returned by the service for retrieving the next page.
        """
        super().__init__(items)
        self.next_page_token = next_page_token if next_page_token is not None else next_link

    @property
    def next_link(self) -> str:
        """Legacy alias for next_page_token."""
        return self.next_page_token

    @next_link.setter
    def next_link(self, value: str) -> None:
        self.next_page_token = value
