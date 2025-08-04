from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app import crud, schemas
from app.schemas import BookRead, BookFilter
from app.models import Base
from app.handlers.external import fetch_and_save_books_handler


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/admin/fetch-and-save-books/", response_model=list[BookRead])
async def fetch_and_save_books_route(
    title: str = Body(..., embed=True, description="Название книги для поиска"),
    password: str = Body(..., embed=True, description="Пароль администратора"),
    db: Session = Depends(get_db)
):
    return await fetch_and_save_books_handler(title=title, password=password, db=db)

@router.get("/books/", response_model=list[BookRead])
async def get_books_by_properties(
    filters: BookFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    from app.handlers.internal import get_books_by_filters
    return await get_books_by_filters(db, filters, skip, limit)

@router.post("/books", response_model=schemas.BookOut)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    from app.handlers.internal import create_book_handler
    return create_book_handler(book, db)

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(book_id: str, book: schemas.BookCreate, db: Session = Depends(get_db)):
    from app.handlers.internal import update_book_handler
    return update_book_handler(book_id, book, db)

@router.delete("/{book_id}")
def delete_book(book_id: str, db: Session = Depends(get_db)):
    from app.handlers.internal import delete_book_handler
    return delete_book_handler(book_id, db)
