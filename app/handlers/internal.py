from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.handlers.external import fetch_books_from_google

async def get_books_by_filters(db: Session, filters, skip: int, limit: int):
    query = db.query(models.Book)

    filter_mapping = {
        "book_id": lambda v: models.Book.id == v,
        "title": lambda v: models.Book.title.ilike(f"%{v}%"),
        "author": lambda v: models.Book.author.ilike(f"%{v}%"),
        "year": lambda v: models.Book.year == v,
    }

    for field, condition in filter_mapping.items():
        value = getattr(filters, field, None)
        if value is not None:
            query = query.filter(condition(value))

    if filters.sort_by_created_at:
        if filters.sort_by_created_at == "old":
            query = query.order_by(models.Book.created_at.asc())
        elif filters.sort_by_created_at == "new":
            query = query.order_by(models.Book.created_at.desc())

    results = query.offset(skip).limit(limit).all()

    if results:
        return results

    if filters.title or filters.author or filters.year:
        return await fetch_books_from_google(
            title=filters.title,
            author=filters.author,
            year=filters.year,
            limit=limit
        )

    raise HTTPException(status_code=404, detail="Книги не найдены")


def create_book_handler(book: schemas.BookCreate, db: Session) -> schemas.BookOut:
    if not book.title or not book.author:
        raise HTTPException(status_code=422, detail="Название книги и автор обязательны")

    new_book = models.Book(
        title=book.title,
        author=book.author,
        year=book.year
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


def update_book_handler(book_id: str, book: schemas.BookCreate, db: Session):
    updated = crud.update_book(db, book_id, book)
    if updated is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return updated


def delete_book_handler(book_id: str, db: Session):
    deleted = crud.delete_book(db, book_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return {"message": "Книга удалена"}
