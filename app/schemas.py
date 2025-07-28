from pydantic import BaseModel
from typing import Optional, Literal

class BookBase(BaseModel):
    title: str
    author: str
    year: int | None = None

class BookFilter(BaseModel):
    book_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    sort_by_created_at: Optional[Literal["new", "old"]] = None

class BookCreate(BaseModel):
    title: str
    author: str
    year: int | None = None

class Book(BookBase):
    id: str

class BookOut(BookCreate):
    id: str

    class Config:
        orm_mode = True

class BookRead(BaseModel):
    id: str
    title: str
    author: str
    year: Optional[int] = None

    class Config:
        orm_mode = True