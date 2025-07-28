import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import HTTPException
from app.handlers import fetch_books_from_google, get_books_by_filters
from app.schemas import BookRead
from app import models, schemas
from app.handlers import create_book_handler, update_book_handler

@pytest.fixture
def mock_filters_with_title():
    class Filters:
        title = "Python"
        book_id = None
        author = None
        year = None
        sort_by_created_at = None
    return Filters()

@pytest.fixture
def mock_filters_for_db():
    class Filters:
        title = None
        book_id = None
        author = "Guido"
        year = 2020
        sort_by_created_at = "new"
    return Filters()

@pytest.fixture
def mock_db_with_books():
    fake_query = MagicMock()
    fake_query.filter.return_value = fake_query
    fake_query.order_by.return_value = fake_query
    fake_query.offset.return_value = fake_query
    fake_query.limit.return_value = fake_query
    fake_query.all.return_value = ["book1", "book2"]

    fake_db = MagicMock()
    fake_db.query.return_value = fake_query
    return fake_db

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_fetch_books_from_google_success(mock_get):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={
        "items": [
            {
                "id": "1",
                "volumeInfo": {
                    "title": "Test Book",
                    "authors": ["Author A", "Author B"],
                    "publishedDate": "2020-01-01"
                }
            }
        ]
    })
    mock_get.return_value = mock_response

    result = await fetch_books_from_google("Test", limit=1)

    assert isinstance(result, list)
    assert len(result) == 1
    book = result[0]
    assert isinstance(book, BookRead)
    assert book.title == "Test Book"
    assert book.author == "Author A, Author B"
    assert book.year == 2020

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_fetch_books_from_google_failure_status(mock_get):
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.json = AsyncMock(return_value={})
    mock_get.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        await fetch_books_from_google("Fail test")

    assert exc_info.value.status_code == 502
    assert "Ошибка при запросе" in exc_info.value.detail

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_fetch_books_from_google_no_items(mock_get):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value={})
    mock_get.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        await fetch_books_from_google("empty")

    assert exc_info.value.status_code == 404
    assert "Книги не найдены" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_books_by_filters_uses_google(monkeypatch, mock_filters_with_title):
    mock_result = [BookRead(id="x", title="T", author="A", year="2020", created_at=datetime.utcnow())]

    async def mock_google(title, limit=5):
        return mock_result

    monkeypatch.setattr("app.handlers.fetch_books_from_google", mock_google)

    fake_db = MagicMock()

    result = await get_books_by_filters(fake_db, mock_filters_with_title, skip=0, limit=5)

    assert result == mock_result


@pytest.mark.asyncio
async def test_get_books_by_filters_db_query(mock_db_with_books, mock_filters_for_db):
    result = await get_books_by_filters(mock_db_with_books, mock_filters_for_db, skip=0, limit=10)

    assert result == ["book1", "book2"]
    assert mock_db_with_books.query.called
    mock_db_with_books.query.return_value.filter.assert_called()
    mock_db_with_books.query.return_value.order_by.assert_called()


@pytest.mark.asyncio
async def test_get_books_by_filters_empty_result_raises_404(monkeypatch):
    class EmptyFilters:
        title = None
        book_id = None
        author = None
        year = None
        sort_by_created_at = None

    fake_query = MagicMock()
    fake_query.filter.return_value = fake_query
    fake_query.order_by.return_value = fake_query
    fake_query.offset.return_value = fake_query
    fake_query.limit.return_value = fake_query
    fake_query.all.return_value = []

    fake_db = MagicMock()
    fake_db.query.return_value = fake_query

    with pytest.raises(HTTPException) as exc_info:
        await get_books_by_filters(fake_db, EmptyFilters(), skip=0, limit=5)

    assert exc_info.value.status_code == 404
    assert "Книги не найдены" in exc_info.value.detail

def test_create_book_handler_success():
    book_create = schemas.BookCreate(title="Test Book", author="Test Author", year=2023)

    mock_db = MagicMock()

    result = create_book_handler(book_create, mock_db)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    assert isinstance(result, models.Book)
    assert result.title == "Test Book"
    assert result.author == "Test Author"
    assert result.year == 2023

def test_create_book_handler_missing_title_or_author():
    mock_db = MagicMock()

    book_create1 = schemas.BookCreate(title="", author="Author", year=2023)
    with pytest.raises(HTTPException) as exc:
        create_book_handler(book_create1, mock_db)
    assert exc.value.status_code == 422

    book_create2 = schemas.BookCreate(title="Title", author="", year=2023)
    with pytest.raises(HTTPException) as exc:
        create_book_handler(book_create2, mock_db)
    assert exc.value.status_code == 422

def test_update_book_handler_success():
    book_data = schemas.BookCreate(title="Updated Title", author="Updated Author", year=2025)
    book_id = "some-book-id"

    updated_book = models.Book(id=book_id, title="Updated Title", author="Updated Author", year=2025)

    mock_db = MagicMock()

    with patch("app.handlers.crud.update_book", return_value=updated_book) as mock_update:
        result = update_book_handler(book_id, book_data, mock_db)

        mock_update.assert_called_once_with(mock_db, book_id, book_data)

        assert result == updated_book
        assert result.title == "Updated Title"
        assert result.author == "Updated Author"

def test_update_book_handler_not_found():
    book_data = schemas.BookCreate(title="New Title", author="New Author", year=2024)
    book_id = "nonexistent-id"
    mock_db = MagicMock()

    with patch("app.handlers.crud.update_book", return_value=None):
        with pytest.raises(HTTPException) as exc:
            update_book_handler(book_id, book_data, mock_db)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Книга не найдена"

def test_update_book_handler_success():
    book_data = schemas.BookCreate(title="Updated Title", author="Updated Author", year=2025)
    book_id = "some-book-id"

    updated_book = models.Book(id=book_id, title="Updated Title", author="Updated Author", year=2025)

    mock_db = MagicMock()

    with patch("app.handlers.crud.update_book", return_value=updated_book) as mock_update:
        result = update_book_handler(book_id, book_data, mock_db)

        mock_update.assert_called_once_with(mock_db, book_id, book_data)

        assert result == updated_book
        assert result.title == "Updated Title"
        assert result.author == "Updated Author"

def test_update_book_handler_not_found():
    book_data = schemas.BookCreate(title="New Title", author="New Author", year=2024)
    book_id = "nonexistent-id"
    mock_db = MagicMock()

    with patch("app.handlers.crud.update_book", return_value=None):
        with pytest.raises(HTTPException) as exc:
            update_book_handler(book_id, book_data, mock_db)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Книга не найдена"