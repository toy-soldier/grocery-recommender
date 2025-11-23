"""This module defines the Product model for the sqlmodel ORM."""

from collections.abc import Sequence
from typing import Self

from fastapi import HTTPException
from sqlmodel import Session, select

from apps.api_server.dependencies import constants
from apps.api_server.schemas import products


class Products(products.ProductDetails, table=True):
    """
    ORM class for `products` table.
    Inherits the fields from `ProductDetails` schema to avoid code duplication.
    """

    @classmethod
    def retrieve(cls, session: Session, product_id: int) -> Self:
        """The Retrieve operation."""
        existing_obj = session.get(cls, product_id)
        if not existing_obj:
            raise HTTPException(status_code=404, detail=constants.ERROR_NOT_FOUND)
        return existing_obj

    @classmethod
    def listing(
        cls, session: Session, offset: int, limit: int
    ) -> tuple[Sequence[Self], bool]:
        """The Listing operation."""
        # fetch an extra record, to check whether there is another page of results
        fetched_records = session.exec(
            select(cls).order_by(cls.sku).offset(offset).limit(limit + 1)
        ).all()
        return fetched_records[:limit], len(fetched_records) > limit
