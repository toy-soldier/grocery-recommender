"""This module defines the Pydantic models."""

from pydantic import BaseModel, Field


class ProductLineItem(BaseModel):
    """Schema for a product entry."""

    description: str
    sku: int


class ProductCatalog(BaseModel):
    """Schema for the store catalog."""

    catalog: list[ProductLineItem]


class ParsedLineItem(BaseModel):
    """Schema for a line parsed from the user's grocery list."""

    query: str
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


class PrunedCatalogPerGroceryListLine(ParsedLineItem):
    """Schema of the per-line subset of the store catalog."""

    candidates: list[ProductLineItem] = Field(default_factory=list)


class PrunedCatalogList(BaseModel):
    """
    Schema for the data to be forwarded to the recommender;
    populated by the fuzzy filter service.
    """

    lines: list[PrunedCatalogPerGroceryListLine]


class LLMRecommendationLineItem(ProductLineItem):
    """Schema for a product recommendation."""

    confidence: float


class LLMRecommendationListPerGroceryListLine(BaseModel):
    """Schema for the per-line recommendations."""

    query: str
    recommendations: list[LLMRecommendationLineItem]


class LLMRecommendationList(BaseModel):
    """Schema for the recommender service's recommendation list."""

    recommendations: list[LLMRecommendationListPerGroceryListLine]


class AgentRecommendationLineItem(LLMRecommendationLineItem):
    """Schema for a product recommendation from the agent."""

    quantity: int
    unit_price: float


class AgentRecommendationListPerGroceryListLine(BaseModel):
    """Schema for the per-line recommendations."""

    query: str
    suggestions: list[AgentRecommendationLineItem]


class AgentRecommendationList(BaseModel):
    """Schema for the agent's final recommendation list."""

    recommendations: list[AgentRecommendationListPerGroceryListLine]
