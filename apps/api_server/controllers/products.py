"""This module defines the functions called when the routes in routers/products.py are invoked."""

from collections.abc import Sequence

from sqlmodel import Session

from apps.api_server.models import products


def retrieve_product(session: Session, product_id: int) -> products.Products:
    """Retrieve a single product."""
    return products.Products.retrieve(session, product_id)


def retrieve_listing(
    session: Session, page: int, products_per_page: int, route_of_listing: str
) -> tuple[Sequence[products.Products], dict[str, int | str | None]]:
    """Retrieve a list of products."""
    limit = products_per_page
    offset = (page - 1) * limit
    fetched_records, has_more = products.Products.listing(session, offset, limit)
    fetch_metadata = {
        "count": len(fetched_records),
        "previous": route_of_listing.format(page - 1, limit) if page > 1 else None,
        "next": route_of_listing.format(page + 1, limit) if has_more else None,
    }
    return fetched_records, fetch_metadata
