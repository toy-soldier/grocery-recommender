"""This is the main module of the API server application."""

from fastapi import FastAPI, status
import uvicorn

from apps.api_server.routers import products

app = FastAPI()

app.include_router(products.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def home() -> dict[str, str]:
    """Handle GET method."""
    return {"message": "This is the application's homepage."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
