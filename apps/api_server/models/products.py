"""This module defines the Product model for the sqlmodel ORM."""

from sqlmodel import Field, SQLModel


class Products(SQLModel, table=True):
    """ORM class for `products` table."""

    sku: int = Field(primary_key=True)
    brand: str = Field()
    description: str = Field()
    unit_price: float = Field()
    qty_in_stock: int = Field()
