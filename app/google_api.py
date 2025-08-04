import httpx
from fastapi import HTTPException
from app.schemas import BookRead

async def fetch_books_from_google(title: str, limit: int = 5) -> list[BookRead]:
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": title, "maxResults": limit}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Ошибка при запросе")

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
        books.append(book)

    if not books:
        raise HTTPException(status_code=404, detail="Книги не найдены")

    return books
