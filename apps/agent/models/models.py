"""This module defines the Pydantic models."""

from pydantic import BaseModel


class ProductLineItem(BaseModel):
    """Schema for a product entry."""

    description: str
    sku: int


class ProductCatalog(BaseModel):
    """Schema for the store catalog."""

    catalog: list[ProductLineItem]


class ParsedLineItem(BaseModel):
    """Schema for a line parsed from the user's grocery list."""

    product: str
    quantity: float | None = None
    unit: str | None = None


class ParsedGroceryList(BaseModel):
    """Schema for the parsed grocery list."""

    grocery_list: list[ParsedLineItem]


class CatalogForFuzzyMatching(BaseModel):
    """Schema of the data to be forwarded to the fuzzy matching service."""

    catalog: ProductCatalog
    grocery_list: ParsedGroceryList


class PrunedCatalog(ProductCatalog):
    """Schema of the subset of the store catalog."""

    pass


class CatalogForRecommendation(BaseModel):
    """Schema for the data to be forwarded to the recommendation service."""

    catalog: PrunedCatalog
    grocery_list: ParsedGroceryList


class RecommendationLineItem(ProductLineItem):
    """Schema for a product recommendation."""

    confidence: float


class RecommendationList(BaseModel):
    """Schema for the recommendations of the recommendation service."""

    recommendations: list[RecommendationLineItem]
