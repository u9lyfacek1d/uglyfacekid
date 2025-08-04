from fastapi import HTTPException
import httpx
from sqlalchemy.orm import Session
from app.schemas import BookRead
from app.models import Book
from app.google_api import fetch_books_from_google

ADMIN_PASSWORD = "123"

async def fetch_and_save_books_handler(
    title: str | None,
    author: str | None,
    year: str | None,
    password: str,
    db: Session
) -> list[BookRead]:
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    books = await fetch_books_from_google(title=title, author=author, year=year, limit=5)

    saved_books = []
    for book_data in books:
        exists = db.query(Book).filter(Book.id == book_data.id).first()
        if exists:
            saved_books.append(exists)
            continue

        new_book = Book(
            id=book_data.id,
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
        )
        db.add(new_book)
        saved_books.append(new_book)

    db.commit()
    return saved_books

async def fetch_books_from_google(
    title: str = None,
    author: str = None,
    year: str = None,
    limit: int = 5
) -> list[BookRead]:
    url = "https://www.googleapis.com/books/v1/volumes"

    q_parts = []
    if title:
        q_parts.append(f'intitle:{title}')
    if author:
        q_parts.append(f'inauthor:{author}')
    if year:
        q_parts.append(f'inpublisher:{year}')

    if not q_parts:
        raise HTTPException(status_code=400, detail="Не указано ни одного параметра поиска")

    query = " ".join(q_parts)
    params = {"q": query, "maxResults": limit}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Ошибка при запросе к Google Books API")

    data = await response.json()
    books = []

    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        book = BookRead(
            id=item.get("id", ""),
            title=info.get("title", "Без названия"),
            author=", ".join(info.get("authors", ["Неизвестный автор"])),
            year=info.get("publishedDate", "")[:4],
        )
        if year and book.year != year:
            continue
        books.append(book)

    if not books:
        raise HTTPException(status_code=404, detail="Книги не найдены")

    return books
