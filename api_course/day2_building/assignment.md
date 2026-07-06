# Assignment: Task Manager API

Build a Task Manager API from scratch. This combines everything from Day 2: routes, path params, query params, request bodies, validation, error handling, and CRUD operations.

## Specifications

Each task has:

| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Auto-generated, read-only |
| `title` | str | Required, at least 1 character |
| `description` | str | Optional, defaults to "" |
| `completed` | bool | Defaults to false |
| `priority` | int | 1 to 5, defaults to 3 |

## Endpoints

| Method | Path | Status | Notes |
|--------|------|--------|-------|
| GET | `/tasks` | 200 | Optional: `?completed=true&priority=3` |
| GET | `/tasks/{id}` | 200 / 404 | Returns one task or error |
| POST | `/tasks` | 201 | Body: title, description, completed, priority |
| PUT | `/tasks/{id}` | 200 / 404 | Partial update, only sent fields change |
| DELETE | `/tasks/{id}` | 204 / 404 | No response body |

## Validation requirements

- `title` must be at least 1 character
- `priority` must be between 1 and 5 (use `@field_validator`)
- Return 404 with a clear message when a task doesn't exist
- Return 422 with field-level errors when validation fails

## Starter

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    description: str = ""
    completed: bool = False
    priority: int = 3

class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = ""
    completed: bool = False
    priority: int = 3

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    completed: bool | None = None
    priority: int | None = None

# Add priority validator to TaskCreate and TaskUpdate

tasks_db: list[Task] = []
next_id = 1

# Implement all five endpoints
```

## Testing

Run with `uvicorn main:app --reload` and test in `/docs`:

1. Create 3 tasks with different priorities
2. List all tasks
3. Filter by priority
4. Get a single task
5. Update a task's title and completed status
6. Delete a task
7. Try to get the deleted task (should return 404)
8. Try creating a task with priority 6 (should return 422)
9. Try creating a task with an empty title (should return 422)

## Bonus

- `GET /tasks/stats` — return total, completed, pending count, average priority
