# Lesson 1: Your First API

An API is a bridge between two pieces of software. One side sends a request, the other sends back a response. The most common kind of API on the web is REST, which uses HTTP as its language. When you type a URL into your browser, you're making an HTTP request. The server sends back HTML. An API does the same thing, but instead of HTML it sends JSON — structured data that programs can understand.

## What FastAPI does

FastAPI is a Python framework that makes it easy to build these APIs. At its heart, it's a mapping between URLs and functions. You write a function, attach a URL to it with a decorator, and when someone visits that URL, the function runs and its return value is sent back as JSON.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, world!"}
```

The decorator `@app.get("/")` is where the magic happens. It registers the function `home` as the handler for GET requests to the root path `/`. The `app` object is your entire application — it holds all your routes, configuration, and middleware.

FastAPI automatically converts the dictionary you return into JSON. You don't need to call `json.dumps()` or set content-type headers. It also sets the HTTP status code to 200 by default, which means "OK."

## Running the server

Python code doesn't run by itself. You need a server to listen for HTTP requests and feed them to your FastAPI app. That's what Uvicorn does:

```bash
uvicorn main:app --reload
```

The `--reload` flag watches your files for changes and restarts the server automatically. Without it, you'd have to stop and start the server after every edit. This is essential during development but should never be used in production.

`main:app` means "look in the file `main.py` for the variable `app`." The file name comes from your Python file (without the `.py` extension), and `app` is whatever you named your FastAPI instance.

## How the request-response cycle works

When a client makes a request to `http://localhost:8000/items`, here's what happens:

1. Uvicorn receives the raw HTTP request
2. It passes the request to FastAPI
3. FastAPI looks at the HTTP method (GET) and the path (`/items`)
4. It finds the matching route handler function
5. It calls that function
6. The function returns a Python dictionary
7. FastAPI converts it to JSON
8. FastAPI wraps it in an HTTP response with status code 200 and content-type `application/json`
9. Uvicorn sends the response back to the client

Understanding this cycle is important because every framework does the same thing, just with different syntax.

## Status codes

Every HTTP response includes a status code — a three-digit number that tells the client what happened. The codes are grouped by category:

- **2xx** — Success. Everything worked. 200 means OK, 201 means Created.
- **3xx** — Redirection. The resource moved.
- **4xx** — Client error. You sent something wrong. 404 means Not Found.
- **5xx** — Server error. Something broke on our end.

FastAPI defaults to 200 for GET requests, but you can set it explicitly:

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy"}
```

The `status` module provides named constants like `HTTP_200_OK`, `HTTP_201_CREATED`, `HTTP_404_NOT_FOUND`. Using these instead of raw numbers makes your code self-documenting.

## Interactive documentation

One of FastAPI's best features is automatic documentation. Because you used type hints and decorators, FastAPI knows everything about your API — the routes, the parameters, the response format — and it generates two sets of docs:

- **Swagger UI** at `/docs` — an interactive page where you can test every endpoint
- **ReDoc** at `/redoc` — a clean, readable reference

Open `http://127.0.0.1:8000/docs` after starting your server. You'll see all your routes listed. Click on one, then click "Try it out" to send a real request and see the response. This is the best way to test your API during development.

## Putting it together

Your first API should have four endpoints. Each one teaches a different aspect of how FastAPI works:

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.get("/")
def home():
    """Returns a simple greeting."""
    return {"message": "Hello, world!"}


@app.get("/info")
def info():
    """Returns metadata about the API."""
    return {"app": "My First API", "version": "1.0.0"}


@app.get("/items")
def items():
    """Returns a list of items. Demonstrates returning arrays."""
    return [
        {"id": 1, "name": "Laptop", "price": 999.99},
        {"id": 2, "name": "Mouse", "price": 29.99},
    ]


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    """Returns health status with explicit 200 status."""
    return {"status": "healthy"}
```

Run this with `uvicorn main:app --reload`, then visit each URL in your browser. Open `/docs` and test all four endpoints. Notice how each one returns JSON automatically, how the status code appears in the response, and how the docs page knows exactly what each endpoint returns.
