from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import uuid
from app.main import app
from app.models import Base, Book
from app.database import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_books_search():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    book = Book(
        id=str(uuid.uuid4()),
        title="uglyfacekid",
        author="me",
        year=666
    )
    db.add(book)
    db.commit()
    db.close()
    #proverka po title and author
    response = client.get("/books/", params={"title": "ugly"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "uglyfacekid"
    assert data[0]["author"] == "me"
    #proverka error
    response = client.get("/books/", params={"title": "пусто типо ахахахах"})
    assert response.status_code == 404
    assert response.json() == {"detail": "По вашему запросу книг не найдено"}

def test_create_book():
    Base.metadata.create_all(bind=engine)

    book = {
        "title": "Test Book",
        "author": "Test Author",
        "year": 2024
    }

    response = client.post("/books", json=book)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == book["title"]
    assert data["author"] == book["author"]
    assert data["year"] == book["year"]
    assert "id" in data

def test_update_book():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    book = Book(
        id=str(uuid.uuid4()),
        title="beautifulfacekid",
        author="u",
        year=2025
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    db.close()

    newbook = {
        "title": "uglyfacekid",
        "author": "me",
        "year": 666
    }
    response = client.put(f"/{book.id}", json=newbook)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book.id
    assert data["title"] == newbook["title"]
    assert data["author"] == newbook["author"]
    assert data["year"] == newbook["year"]

    fake_id = str(uuid.uuid4())
    response = client.put(f"/{fake_id}", json=newbook)
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"


def test_delete_book():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    book = Book(
        id=str(uuid.uuid4()),
        title="Delete Me",
        author="Author",
        year=2025
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    db.close()

    response = client.delete(f"/{book.id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Книга удалена"}

    fake_id = str(uuid.uuid4())
    response = client.delete(f"/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Книга не найдена"