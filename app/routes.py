from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app import crud, schemas, models
from app.schemas import BookCreate, BookOut
from app.models import Book, Base

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.get("/books/")
def get_books_by_properties(
    book_id: str | None = None,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if book_id:
        query = query.filter(Book.id == book_id)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if year is not None:
        query = query.filter(Book.year == year)

    results = query.offset(skip).limit(limit).all()

    if not results:
        raise HTTPException(status_code=404, detail="По вашему запросу книг не найдено")

    return results


@router.post("/books", response_model=BookOut)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
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

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: str, book: schemas.BookCreate, db: Session = Depends(get_db)):
    updated = crud.update_book(db, book_id, book)
    if updated is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return updated

@router.delete("/{book_id}")
def delete_book(book_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_book(db, book_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return {"message": "Книга удалена"}

