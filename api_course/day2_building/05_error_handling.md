# Lesson 5: Error Handling and Validation

Every API receives bad requests. Clients send the wrong data, request resources that don't exist, or trigger edge cases the developer didn't anticipate. How you handle these situations determines whether your API is frustrating or helpful.

Good error handling means:

- **Clear messages** — tell the client exactly what went wrong
- **Correct status codes** — use the right HTTP status for each situation
- **Consistent format** — errors should look the same every time
- **Early rejection** — fail fast before processing bad data

## HTTPException

FastAPI's primary error mechanism is `HTTPException`. It's a Python exception that, when raised, immediately stops the function and returns an error response:

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

ITEMS = {1: "Laptop", 2: "Mouse"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return {"id": item_id, "name": ITEMS[item_id]}
```

When the client requests a non-existent item, FastAPI returns:

```json
{
  "detail": "Item 99 not found"
}
```

The `detail` field is the standard FastAPI error format. You can make it a string, a dict, or a list. The `status_code` determines the HTTP status. Every error should use the most specific status code available:

- **404** — resource doesn't exist
- **400** — bad request (malformed data)
- **401** — not authenticated
- **403** — authenticated but not authorized
- **409** — conflict (e.g., duplicate resource)
- **422** — validation error (Pydantic handles this automatically)

## Custom headers in errors

Some HTTP errors require specific headers. The most common example is 401 Unauthorized, which should include a `WWW-Authenticate` header telling the client how to authenticate:

```python
@app.get("/secure")
def secure():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )
```

The client reads the `WWW-Authenticate` header and knows to send a Bearer token. Without this header, the client has no way of knowing what authentication method the API expects.

## Field-level validation

Pydantic catches many errors before your function even runs. The `Field` function adds constraints to model fields:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: int = Field(ge=0, le=150)
```

The constraints are self-explanatory:

- `min_length=3` — username must be at least 3 characters
- `max_length=20` — username can be at most 20 characters
- `ge=0` — age must be greater than or equal to 0
- `le=150` — age must be less than or equal to 150

These constraints apply to numeric types as well as strings. `ge`, `gt`, `le`, `lt` work on `int` and `float` fields. `min_length` and `max_length` work on `str` fields.

When validation fails, FastAPI returns a 422 response with a detailed error body:

```json
{
  "detail": [
    {
      "loc": ["body", "age"],
      "msg": "Input should be less than or equal to 150",
      "type": "less_than_equal"
    }
  ]
}
```

Each error in the list includes the field location (`loc`), a human-readable message (`msg`), and an error type (`type`). This structured format lets clients display field-level errors alongside form inputs.

## Custom field validators

Sometimes built-in constraints aren't enough. You need to check relationships between fields or apply business rules. Pydantic's `@field_validator` decorator lets you write custom validation logic:

```python
from pydantic import field_validator

class Review(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str = ""

    @field_validator("comment")
    @classmethod
    def no_prohibited_words(cls, v):
        prohibited = ["spam", "advertisement"]
        for word in prohibited:
            if word in v.lower():
                raise ValueError(f"Comment contains: {word}")
        return v
```

The validator is a class method (hence `@classmethod`) that receives the value of the field being validated. If the value is invalid, raise `ValueError` with a message. If valid, return the value.

The validator runs after type checking but before the model is constructed. This means you can assume the value has the correct type but not that it's semantically valid.

## Path parameter validation

Pydantic's `Field` only works on body fields. For path parameters, FastAPI provides its own `Path` function:

```python
from fastapi import Path

@app.get("/articles/{year}/{month}")
def get_articles(
    year: int = Path(ge=2000, le=2030),
    month: int = Path(ge=1, le=12)
):
    return {"year": year, "month": month}
```

The syntax is identical to `Field`, but this applies to values extracted from the URL path. A request to `/articles/1999/13` returns a 422 error because 1999 is below 2000 and 13 is above 12.

## Global exception handlers

By default, unhandled exceptions in FastAPI return a 500 Internal Server Error with a generic message. You can customize this by registering exception handlers:

```python
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def handle_value_error(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": True, "message": str(exc)}
    )

@app.get("/divide/{a}/{b}")
def divide(a: int, b: int):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return {"result": a / b}
```

Now any `ValueError` raised anywhere in your application returns a consistent JSON error response instead of a raw traceback. The exception handler receives the request object and the exception instance, and returns a response.

## Building the lesson

Create `main.py`:

```python
from fastapi import FastAPI, HTTPException, status, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


ITEMS = {1: "Laptop", 2: "Mouse"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in ITEMS:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return {"id": item_id, "name": ITEMS[item_id]}


@app.get("/secure")
def secure():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )


class User(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: str
    age: int = Field(ge=0, le=150)


@app.post("/users")
def create_user(user: User):
    return {"message": f"User {user.username} created"}


class Review(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str = ""

    @field_validator("comment")
    @classmethod
    def no_prohibited(cls, v):
        prohibited = ["spam", "bad"]
        for word in prohibited:
            if word in v.lower():
                raise ValueError(f"Contains: {word}")
        return v


@app.post("/reviews")
def submit_review(review: Review):
    return {"message": "Review accepted"}


@app.get("/articles/{year}/{month}")
def get_articles(year: int = Path(ge=2000, le=2030), month: int = Path(ge=1, le=12)):
    return {"year": year, "month": month}


@app.exception_handler(ValueError)
async def handle_value_error(request, exc):
    return JSONResponse(status_code=400, content={"error": True, "message": str(exc)})


@app.get("/divide/{a}/{b}")
def divide(a: int, b: int):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return {"result": a / b}
```

Run with `uvicorn main:app --reload`. In `/docs`, test each error case: request a non-existent item, submit a user with age 200, submit a review with a prohibited word, request an invalid article date, and divide by zero. Read each error message carefully.
