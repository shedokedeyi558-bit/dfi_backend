# Lesson 3: POST and Data Models

GET requests fetch data. POST requests create data. When you create something, you need to send data to the server — not just in the URL, but in the body of the request. This is where REST APIs get interesting: you need to define what data you expect, validate it, and respond appropriately.

## Why request bodies matter

A URL has length limits. Browsers and servers restrict URLs to a few thousand characters. Query parameters also have type limitations — everything is a string until you parse it. For complex data like a user registration form or an order with multiple items, you need a request body.

The request body is the payload of an HTTP request. It's separate from the URL and can carry structured data in formats like JSON, XML, or form data. Almost every modern API uses JSON.

## Pydantic models

FastAPI uses Pydantic to define and validate request bodies. A Pydantic model is a Python class that describes the shape of your data:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    tax: float = 0.0
    description: str | None = None
```

Each attribute is a field with a type. The type serves two purposes: it tells FastAPI what kind of data to expect, and it tells Pydantic how to validate the incoming JSON.

- `name: str` — Required. Must be a string. If missing or not a string, validation fails.
- `price: float` — Required. Must be a number. Converts integers to floats automatically.
- `tax: float = 0.0` — Optional. Defaults to 0.0 if not provided. The client can omit it.
- `description: str | None = None` — Optional. Can be a string or null. Defaults to None.

The `| None` syntax (Python 3.10+) means the field accepts `None` as a valid value. This is different from just having a default — it explicitly says "null is allowed here."

When the client sends `{"name": "Keyboard", "price": 79.99}`, Pydantic creates an `Item` object with `tax=0.0` and `description=None`. When the client sends `{"name": "Keyboard", "price": "hello"}`, Pydantic raises a validation error because `"hello"` cannot be converted to a float.

## Using the model in an endpoint

You use a Pydantic model as a parameter type hint in your endpoint function:

```python
from fastapi import FastAPI, status

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    tax: float = 0.0

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    total = item.price + item.tax
    return {"id": 1, "name": item.name, "total": total}
```

FastAPI recognizes that `Item` is a Pydantic model and reads the request body as JSON. It validates the JSON against the model and passes you a fully populated `Item` object. You never deal with raw dictionaries or manual JSON parsing.

The status code `201 Created` is the correct response for POST requests. It tells the client that a new resource was created, as opposed to 200 which just means "the request succeeded."

Test with curl:

```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Keyboard", "price": 79.99, "tax": 8.00}'
```

Or use `/docs` — FastAPI's Swagger UI shows a JSON editor for POST endpoints with the exact schema your model defines. It even generates example values.

## Mixing parameter sources

Path parameters, query parameters, and request bodies can all appear in the same endpoint. FastAPI distinguishes them by type:

```python
from datetime import datetime

class Order(BaseModel):
    product_id: int
    quantity: int
    note: str = ""

@app.post("/users/{user_id}/orders", status_code=status.HTTP_201_CREATED)
def place_order(user_id: int, order: Order, coupon: str = ""):
    return {
        "order_id": 100,
        "user_id": user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "coupon": coupon,
        "total": order.quantity * 49.99,
        "created_at": datetime.now().isoformat()
    }
```

FastAPI uses these rules to decide where each parameter comes from:

1. If the parameter name appears in the path with curly braces → path parameter
2. If the parameter is a Pydantic `BaseModel` subclass → request body
3. Otherwise → query parameter

This is why you don't need special annotations for request bodies. The type system handles it.

## Response models

Pydantic models can also describe what your API returns. This is useful for consistency and documentation:

```python
class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(username: str, email: str):
    return UserOut(id=42, username=username, email=email, is_active=True)
```

The `response_model` parameter tells FastAPI:

- What schema to show in the docs
- What fields to include in the response
- What types to convert to

If your function accidentally returns extra fields, `response_model` filters them out. This prevents leaking internal data.

## Building the lesson

Create `main.py`:

```python
from fastapi import FastAPI, status
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    tax: float = 0.0


class Order(BaseModel):
    product_id: int
    quantity: int
    note: str = ""


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool


@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    total = item.price + item.tax
    return {"id": 1, "name": item.name, "total": total}


@app.post("/users/{user_id}/orders", status_code=status.HTTP_201_CREATED)
def place_order(user_id: int, order: Order, coupon: str = ""):
    return {
        "order_id": 100,
        "user_id": user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "coupon": coupon,
        "total": order.quantity * 49.99,
        "created_at": datetime.now().isoformat()
    }


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(username: str, email: str):
    return UserOut(id=42, username=username, email=email, is_active=True)
```

Run with `uvicorn main:app --reload`. In `/docs`, test each POST endpoint. Try sending incomplete data, wrong types, and extra fields. Observe how FastAPI responds to each case.
