from sqlalchemy.orm import Session
from . import models, schemas

def get_book(db: Session, book_id: str):
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Book).offset(skip).limit(limit).all()

def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(title=book.title, author=book.author, year=book.year)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def update_book(db: Session, book_id: str, book: schemas.BookCreate):
    db_book = get_book(db, book_id)
    if db_book is None:
        return None
    db_book.title = book.title
    db_book.author = book.author
    db_book.year = book.year
    db.commit()
    db.refresh(db_book)
    return db_book

def delete_book(db: Session, book_id: str):
    db_book = get_book(db, book_id)
    if db_book is None:
        return None
    db.delete(db_book)
    db.commit()
    return db_book
