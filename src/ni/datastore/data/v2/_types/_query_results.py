"""Query results data type for the V2 Data Store Client."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


class QueryResults(list[T]):
    """A list of query results with the service's next-page link."""

    next_link: str
    """The OData link to the next page of results, or an empty string on the last page."""

    def __init__(self, items: Iterable[T] = (), next_link: str = "") -> None:
        """Initialize a QueryResults instance.

        Args:
            items: The results on this page.
            next_link: The OData link to the next page, or an empty string.
        """
        super().__init__(items)
        self.next_link = next_link
