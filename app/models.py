from sqlalchemy import Column, String, Integer, create_engine, DateTime
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()

class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=True)


engine = create_engine("sqlite:///./test.db", echo=True)
Base.metadata.create_all(bind=engine)
