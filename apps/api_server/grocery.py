"""This is the main module of the API server application."""

import uvicorn
from fastapi import FastAPI, status

from apps.api_server.routers import products

app = FastAPI()

app.include_router(products.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def home() -> dict[str, str]:
    """Handle requests for the homepage."""
    return {"message": "This is the application's homepage."}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    """Handle health queries."""
    return {"message": "All is well."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
