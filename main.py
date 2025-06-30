from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI()

class Book(BaseModel):
    id: str
    title: str
    author: str
    year: int | None = None

class CreateBook(BaseModel):
    title: str
    author: str
    year: int | None = None

books = []

@app.get("/books")
def get_a_list_of_all_books():
    return books

@app.get("/books/{id}")
def get_book_by_id(book_id: str):
    for book in books:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")

@app.post("/books")
def create_book(book: CreateBook):
    new_book = Book(id=str(uuid4()), **book.dict())
    books.append(new_book)
    return new_book

@app.put("/books/{id}")
def update_book(book_id: str, updated_book: CreateBook):
    for index, book in enumerate(books):
        if book.id == book_id:
            books[index] = Book(id=book_id, **updated_book.dict())
            return books[index]
    raise HTTPException(status_code=404, detail="Книга не найдена")

@app.delete("/books/{id}")
def delete_book(book_id: str):
    for index, book in enumerate(books):
        if book.id == book.id:
            del books[index]
            return {"message": "Книга удалена"}
    raise HTTPException(status_code=404, detail="Книга не найдена")

@app.get("/books/")
def get_books(
    title: str | None = None,
    author: str | None = None,
    skip: int = 0,
    limit: int = 10):
    results = books
    if title:
        results = [b for b in results if title.lower() in b.title.lower()]
    if author:
        results = [b for b in results if author.lower() in b.author.lower()]
    return results[skip: skip + limit]
