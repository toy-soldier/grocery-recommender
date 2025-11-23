"""
This module defines the Pydantic models to be used in the `/products` responses.
SQLModel is a SQLAlchemy, and also a Pydantic model.
"""

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    """Base class for Product* classes."""

    sku: int = Field(primary_key=True)
    brand: str = Field()
    description: str = Field()


class ProductDetails(ProductBase):
    """Display a product's complete details."""

    unit_price: float = Field()
    qty_in_stock: int = Field()


class WrappedProductDetails(SQLModel):
    """Schema to use to display a product's details."""

    data: ProductDetails


class ProductShortInfo(SQLModel):
    """Schema to use to display a product's short info."""

    sku: int
    full_name: str


class WrappedProductListing(SQLModel):
    """Schema to use to display a product listing."""

    data: list[ProductShortInfo]
    count: int
    previous: str | None
    next: str | None
