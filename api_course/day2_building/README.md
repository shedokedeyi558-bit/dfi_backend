# Day 2: Building APIs with FastAPI

You've consumed APIs. Now build them.

We'll use FastAPI — a Python framework that turns functions into API endpoints. It validates data, generates docs, and is straightforward to work with.

## Setup

```bash
pip install fastapi uvicorn pydantic
```

## Lessons

| # | File | What you'll learn |
|---|------|-------------------|
| 1 | `01_first_api.md` | Routes, running with uvicorn, status codes |
| 2 | `02_path_query_params.md` | Path parameters, query parameters |
| 3 | `03_request_body.md` | POST requests, Pydantic models |
| 4 | `04_crud_routes.md` | Full CRUD with in-memory storage |
| 5 | `05_error_handling.md` | HTTP errors, validation |

Each lesson builds a file called `main.py`. Run it with:

```bash
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000/docs to test your endpoints.

## Assignment

`assignment.md` — build a Task Manager API from scratch.
