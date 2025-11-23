"""This module defines the API router to handle requests to /stars."""

from fastapi import APIRouter, status, Depends
from sqlmodel import Session

from apps.api_server.controllers import products
from apps.api_server.dependencies import database
from apps.api_server.schemas import products as sp


router = APIRouter(
    prefix="/api/v1/products",
    tags=["products"],
)
route_of_listing = "/?page={0}&products_per_page={1}"


@router.get(path=route_of_listing.split("?")[0], status_code=status.HTTP_200_OK)
async def retrieve_listing(
    page: int = 1,
    products_per_page: int = 50,
    session: Session = Depends(database.get_session),
) -> sp.WrappedProductListing:
    """Handle GET listing request."""
    retrieved_products, metadata = products.retrieve_listing(
        session, page, products_per_page, route_of_listing
    )
    product_listing = []
    for product in retrieved_products:
        product_info = sp.ProductShortInfo(
            sku=product.sku, full_name=product.brand + " " + product.description
        )
        product_listing.append(product_info)
    return sp.WrappedProductListing(
        data=product_listing,
        count=metadata["count"],
        previous=metadata["previous"],
        next=metadata["next"],
    )


@router.get("/{product_id}", status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int, session: Session = Depends(database.get_session)
) -> sp.WrappedProductDetails:
    """Handle GET product request."""
    retrieved_product = products.retrieve_product(session, product_id)
    product_details = sp.ProductDetails.model_validate(retrieved_product)
    return sp.WrappedProductDetails(data=product_details)
