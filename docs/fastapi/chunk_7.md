# fastapi Documentation - Chunk 7

**Original File:** fastapi_hybrid_002_sub_00.md

**Processed with:** ollama (mistral)

---

 # FastAPI Hybrid 0.02 Sub-00

FastAPI is a web framework focused on building efficient, fast APIs with Python. It offers features like automatic type inference, automatic open API documentation, and a developer-friendly approach to API development.

## Configuration

To start using FastAPI, you need to create a new FastAPI instance:

```python
from fastapi import FastAPI
app = FastAPI()
```

You can add routes, middleware, dependencies, and more to this instance as needed. Routes are defined with the `@app.get`, `@app.post`, etc., decorators.

## Usage

Here's a simple example of a FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

You can run this application with the `uvicorn` command, which is provided as part of FastAPI:

```bash
$ uvicorn main:app --host 0.0.0.0 --port 8000
```

FastAPI also supports ASGI and HTTP/2 for better performance.

## Errors

FastAPI provides a simple way to handle errors with the `@app.exception_handler()` decorator:

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 1 or item_id > 100:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"item": f"Item {item_id}"}
```

## Examples

FastAPI has numerous examples in its repository to help you get started with various features like authentication, database connections, testing, and more. You can find them [here](https://github.com/tiangolo/full-stack-fastapi-postgresql).

---

This documentation was extracted from the FastAPI GitHub page ([link](https://github.com/tiangolo/full-stack-fastapi-postgresql)).