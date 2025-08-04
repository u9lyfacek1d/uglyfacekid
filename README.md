FastAPI Книжный каталог с интеграцией Google Books API

Этот проект — API-сервис для работы с книгами. Он позволяет:
- искать и сохранять книги из Google Books API,
- управлять собственным списком книг в базе данных,
- фильтровать и сортировать книги.

Как запустить:
  - Установите зависимости:
      - python -m venv .venv
      - source .venv/bin/activate  #для Linux/Mac
      - .venv\Scripts\activate     #для Windows
      - pip install -r requirements.txt
  - Запустите приложение:
      - uvicorn app.main:app --reload
