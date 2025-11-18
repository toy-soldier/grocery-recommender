"""This module defines the functions called when the routes in routers/products.py are invoked."""


def handle_get(product_id: int) -> dict[str, str | int]:
    """Handle the GET request."""
    return {"input": product_id, "message": "Product successfully retrieved."}


def retrieve_catalog() -> dict[str, str]:
    """Handle the GET request."""
    return {"input": "ALL", "message": "Catalog successfully retrieved."}
