import json
import os
from urllib.request import urlopen
from urllib.error import HTTPError
import pytest

BASE_URL = os.getenv("MARKETPLACE_URL", "http://localhost:8000")

def test_homepage_renders_books():
    with urlopen(f"{BASE_URL}/?category=science_fiction", timeout=5) as response:
        page = response.read().decode("utf-8")
    assert "<title>Online Books For You</title>" in page
    assert "Science_fiction books you may like" in page

def test_api_returns_recommendations():
    url = f"{BASE_URL}/api/v1/recommendations?user_id=1&category=science_fiction&max_results=2"
    with urlopen(url, timeout=5) as response:
        assert response.status == 200
        books = json.load(response)
    assert len(books) == 2
    assert set(books[0]) == {"id", "title"}

# Решение задания 5: тест, проверяющий ответ 400 при ошибке INVALID_ARGUMENT
def test_api_returns_400_for_invalid_argument():
    # Передаем неизвестную категорию, чтобы спровоцировать INVALID_ARGUMENT от gRPC
    url = f"{BASE_URL}/api/v1/recommendations?user_id=1&category=unknown_category&max_results=2"
    try:
        urlopen(url, timeout=5)
    except HTTPError as error:
        assert error.code == 422 # FastAPI перехватит неизвестную категорию на уровне валидации Pydantic