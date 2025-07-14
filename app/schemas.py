from pydantic import BaseModel

class BookBase(BaseModel):
    title: str
    author: str
    year: int | None = None

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