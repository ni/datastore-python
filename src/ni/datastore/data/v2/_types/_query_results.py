"""Query results data type for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


class QueryResults(list[T]):
    """One page of query results with a continuation link when more results exist.

    Page size is not configured by this class; it contains the items and link
    returned by the query.
    """

    next_link: str
    """The link for retrieving the next page, or an empty string when there is none."""

    def __init__(self, items: Iterable[T] = (), next_link: str = "") -> None:
        """Initialize a QueryResults instance.

        Args:
            items: The results on this page.
            next_link: The OData link to the next page, or an empty string.
        """
        super().__init__(items)
        self.next_link = next_link
