import html
import os
from contextlib import asynccontextmanager
from typing import Annotated, Literal
import grpc
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from recommendations_pb2 import BookCategory, RecommendationRequest
from recommendations_pb2_grpc import RecommendationsStub

RECOMMENDATIONS_HOST = os.getenv("RECOMMENDATIONS_HOST", "localhost")
RECOMMENDATIONS_PORT = os.getenv("RECOMMENDATIONS_PORT", "50051")

CategoryName = Literal["mystery", "science_fiction", "self_help"]
CATEGORIES = {
    "mystery": BookCategory.BOOK_CATEGORY_MYSTERY,
    "science_fiction": BookCategory.BOOK_CATEGORY_SCIENCE_FICTION,
}

class BookOut(BaseModel):
    id: int
    title: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    channel = grpc.aio.insecure_channel(f"{RECOMMENDATIONS_HOST}:{RECOMMENDATIONS_PORT}")
    app.state.recommendations = RecommendationsStub(channel)
    yield
    await channel.close()

app = FastAPI(title="Marketplace", lifespan=lifespan)

async def fetch_recommendations(stub, user_id, category, max_results, exclude_ids=None):
    request = RecommendationRequest(
        user_id=user_id, category=CATEGORIES[category], max_results=max_results, exclude_ids=exclude_ids or []
    )
    try:
        response = await stub.Recommend(request, timeout=2.0)
    except grpc.aio.AioRpcError as error:
        if error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=error.details()) from error
        raise HTTPException(status_code=503, detail="Recommendations service is unavailable") from error
    return [BookOut(id=book.id, title=book.title) for book in response.recommendations]

@app.get("/api/v1/recommendations")
async def get_recommendations(
    request: Request, user_id: int, category: CategoryName = "mystery", max_results: Annotated[int, Query(ge=1, le=10)] = 3
):
    return await fetch_recommendations(request.app.state.recommendations, user_id, category, max_results)

# Задание 5
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage(request: Request, category: CategoryName = "mystery"):
    books = await fetch_recommendations(request.app.state.recommendations, user_id=1, category=category, max_results=3)
    items = "\n".join(f"      <li>{html.escape(book.title)}</li>" for book in books)
    return f"""<!doctype html><html><head><title>Online Books For You</title></head><body><h1>{category.capitalize()} books you may like</h1><ul>{items}</ul></body></html>"""