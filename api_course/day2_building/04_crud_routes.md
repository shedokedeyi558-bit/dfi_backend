# Lesson 4: Full CRUD

Most APIs manage resources. A resource is something users create, read, update, and delete — a book, a user, an order, a task. The four operations are so fundamental they have an acronym: CRUD (Create, Read, Update, Delete).

Each CRUD operation maps to an HTTP method and a standard status code:

| Operation | HTTP Method | Success Code | Purpose |
|-----------|-------------|-------------|---------|
| Create | POST | 201 | Make a new resource |
| Read (list) | GET | 200 | Fetch a collection |
| Read (one) | GET | 200 | Fetch a single item |
| Update | PUT / PATCH | 200 | Modify an item |
| Delete | DELETE | 204 | Remove an item |

We'll build a book library API with in-memory storage to see how these operations work together.

## Designing the models

We need three Pydantic models for a CRUD API:

```python
from pydantic import BaseModel

class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    read: bool = False

class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    read: bool = False

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    read: bool | None = None
```

Three separate models feels like repetition, but each serves a different purpose:

- `Book` is the complete object as stored in the system. It has an `id` because every resource needs a unique identifier.
- `BookCreate` defines what the client must send to create a new book. Notice there's no `id` — the server generates that.
- `BookUpdate` defines what the client can send to update a book. Every field is optional because the client may only want to change one thing.

This separation is a common pattern. It lets you enforce different validation rules for creation vs. updates.

## In-memory storage

For learning, we store data in a Python list. In production, you'd use a database, but the API layer looks the same either way:

```python
DB = [
    Book(id=1, title="1984", author="George Orwell", year=1949),
    Book(id=2, title="Brave New World", author="Aldous Huxley", year=1932),
]
next_id = 3
```

`next_id` tracks what ID to assign to the next new book. This is how auto-incrementing IDs work at a basic level.

## Read operations

Reading has two flavors: listing a collection and fetching a single item.

```python
@app.get("/books")
def list_books(author: str | None = None, year: int | None = None):
    results = DB
    if author:
        results = [b for b in results if author.lower() in b.author.lower()]
    if year:
        results = [b for b in results if b.year == year]
    return results
```

The list endpoint returns an array. It supports optional filtering through query parameters. The client can ask for all books, or only books by a certain author, or only books from a certain year. The function always returns 200 with a (possibly empty) array.

```python
@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in DB:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")
```

The single-item endpoint returns the book object on success, or raises a 404 exception. `HTTPException` is FastAPI's mechanism for returning error responses. It stops the function immediately and returns a JSON error body.

Every get-by-ID endpoint must handle the "not found" case. Failing to do so would either return a confusing error or, worse, silently return the wrong data.

## Create operation

```python
from fastapi import status, HTTPException

@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    global next_id
    new_book = Book(id=next_id, **book.model_dump())
    next_id += 1
    DB.append(new_book)
    return new_book
```

Three things happen here:

1. The client sends a `BookCreate` payload. FastAPI validates it against the model.
2. We create a new `Book` with an auto-incremented ID. The client never chooses the ID — that's the server's job.
3. We return the created book with status 201, so the client knows the ID and can verify the data was stored correctly.

The `**book.model_dump()` syntax converts the Pydantic model to a dictionary and spreads it as keyword arguments to the `Book` constructor. It's the standard way to create one model from another.

## Update operation

```python
@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookUpdate):
    for i, existing in enumerate(DB):
        if existing.id == book_id:
            updated = existing.model_copy(update=book.model_dump(exclude_unset=True))
            DB[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Book not found")
```

`model_dump(exclude_unset=True)` returns only the fields that the client actually sent in the request. If the client only sends `{"read": true}`, the result is `{"read": true}` — not a full object with all fields.

`model_copy(update=...)` creates a new Book object with the existing values plus the updates applied. The original object in the database is replaced with the new one.

This approach means updates are partial — the client only sends what it wants to change, and the rest stays the same. Some APIs call this PATCH behavior, but using PUT with partial updates is common in practice.

## Delete operation

```python
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    for i, book in enumerate(DB):
        if book.id == book_id:
            DB.pop(i)
            return
    raise HTTPException(status_code=404, detail="Book not found")
```

DELETE returns 204 with no response body. The 204 status means "the request succeeded and there is no content to return." The client doesn't need to parse a response — it just checks the status code.

If the resource doesn't exist, we return 404 just like with GET.

## Building the lesson

Create `main.py`:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class Book(BaseModel):
    id: int
    title: str
    author: str
    year: int
    read: bool = False

class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    read: bool = False

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    year: int | None = None
    read: bool | None = None


DB = [
    Book(id=1, title="1984", author="George Orwell", year=1949),
    Book(id=2, title="Brave New World", author="Aldous Huxley", year=1932),
]
next_id = 3


@app.get("/books")
def list_books(author: str | None = None, year: int | None = None):
    results = DB
    if author:
        results = [b for b in results if author.lower() in b.author.lower()]
    if year:
        results = [b for b in results if b.year == year]
    return results


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in DB:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate):
    global next_id
    new_book = Book(id=next_id, **book.model_dump())
    next_id += 1
    DB.append(new_book)
    return new_book


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookUpdate):
    for i, existing in enumerate(DB):
        if existing.id == book_id:
            updated = existing.model_copy(update=book.model_dump(exclude_unset=True))
            DB[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    for i, book in enumerate(DB):
        if book.id == book_id:
            DB.pop(i)
            return
    raise HTTPException(status_code=404, detail="Book not found")
```

Run with `uvicorn main:app --reload`. In `/docs`, test the full lifecycle: create a book, list all books, get the new book by ID, update its title, update its read status, then delete it. Try getting it after deletion — you should get 404.
