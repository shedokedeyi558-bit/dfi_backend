# Lesson 2: Parameters

Static routes like `/info` always return the same thing. That's useful for health checks or configuration, but most APIs need to handle dynamic data. When a client says "give me user 42" or "search for items matching python," the server needs to receive input. That input comes through two mechanisms: path parameters and query parameters.

## Path parameters

A URL is more than just an address. It's a structured identifier. Consider this URL:

```
/users/42
```

This isn't just a random string. It follows a pattern: `/users/{id}`. The `42` is a piece of data embedded in the path itself. This is a path parameter — a variable segment of the URL that identifies a specific resource.

In REST APIs, path parameters represent hierarchy and identity. `/users/42/posts/5` means "post number 5 belonging to user number 42." The structure of the URL mirrors the structure of the data.

In FastAPI, you define path parameters with curly braces in the route string:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}
```

The name inside the curly braces (`user_id`) must match the function parameter name. The type hint (`int`) tells FastAPI what type to expect. If someone visits `/users/abc`, FastAPI will reject the request with a 422 validation error before the function even runs. It never calls your function with bad data.

You can have multiple path parameters for nested resources:

```python
@app.get("/users/{user_id}/posts/{post_id}")
def get_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

Each parameter is extracted and validated independently. This works for any number of path segments, as long as each one has a unique name.

Path parameters are not limited to integers. They work with strings too:

```python
@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}
```

## Query parameters

Path parameters identify resources. Query parameters modify how they're returned. They come after the `?` in a URL:

```
/search?q=python&limit=5&page=2
```

Here `q`, `limit`, and `page` are query parameters. They're used for filtering, searching, pagination, and sorting — everything that changes the view of the data without changing which resource you're accessing.

In FastAPI, any function parameter that has a **default value** and is not part of the path becomes a query parameter:

```python
@app.get("/search")
def search(q: str = "", limit: int = 10, offset: int = 0):
    items = ["Python", "FastAPI", "REST", "API", "Backend"]
    results = [item for item in items if q.lower() in item.lower()]
    return {
        "query": q,
        "results": results[offset:offset + limit],
        "total": len(results)
    }
```

The distinction between path and query parameters is simple:

- **No default value, in the path** → path parameter (required)
- **Has a default value** → query parameter (optional)

This is a design choice by FastAPI, and it's one of the reasons the code is so clean. You don't need separate decorators or annotations to distinguish between parameter types.

Try these variations:

| URL | What happens |
|-----|-------------|
| `/search` | Returns all items (q is empty string, limit is 10) |
| `/search?q=api` | Returns only items containing "api" |
| `/search?q=api&limit=1` | Returns only the first match |
| `/search?q=api&offset=1` | Skips the first match |

## Type flexibility in query parameters

Query parameters aren't just strings. FastAPI converts them to whatever type you specify:

```python
@app.get("/products")
def products(
    category: str = "all",
    min_price: float = 0.0,
    max_price: float = 9999.99,
    in_stock: bool = True
):
    return {
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "in_stock": in_stock
    }
```

Visit `/products?category=electronics&min_price=100&in_stock=false`. FastAPI converts `"100"` to `100.0`, `"false"` to `False`, and `"electronics"` to `"electronics"`. If the client sends `min_price=abc`, it returns a validation error.

## Combining both

Path and query parameters work together in the same function. Path parameters identify the resource. Query parameters modify the response:

```python
@app.get("/users/{user_id}/items")
def user_items(user_id: int, sort: str = "name", page: int = 1):
    return {"user_id": user_id, "sort": sort, "page": page, "items": []}
```

Here `user_id` is required and comes from the URL path. `sort` and `page` are optional and come from the query string. FastAPI sorts them out automatically based on the function signature.

This is the standard REST pattern. You'll see it everywhere: `/organizations/{org_id}/repositories?sort=stars&page=2`.

## Building the lesson

Create `main.py` with these endpoints:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/search")
def search(q: str = "", limit: int = 10, offset: int = 0):
    items = ["Python", "FastAPI", "REST", "API", "Backend"]
    results = [item for item in items if q.lower() in item.lower()]
    return {"query": q, "results": results[offset:offset + limit], "total": len(results)}

@app.get("/products")
def products(category: str = "all", min_price: float = 0.0, max_price: float = 9999.99, in_stock: bool = True):
    return {"category": category, "min_price": min_price, "max_price": max_price, "in_stock": in_stock}

@app.get("/users/{user_id}/items")
def user_items(user_id: int, sort: str = "name", page: int = 1):
    return {"user_id": user_id, "sort": sort, "page": page, "items": []}
```

Run with `uvicorn main:app --reload`. Test every endpoint in `/docs`. Pay attention to how FastAPI handles invalid types — try sending a string where an integer is expected and read the error message.
