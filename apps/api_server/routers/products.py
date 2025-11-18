"""This module defines the API router to handle requests to /stars."""

from fastapi import APIRouter, status

from apps.api_server.controllers import products


router = APIRouter(
    prefix="/api/v1/products",
    tags=["products"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def retrieve_catalog() -> dict[str, str]:
    """Handle GET method."""
    return products.retrieve_catalog()


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(product_id: int) -> dict[str, str | int]:
    """Handle GET method."""
    return products.handle_get(product_id)
