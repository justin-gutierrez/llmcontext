# fastapi Documentation - Chunk 2

**Original File:** fastapi_hybrid_000_sub_01.md

**Processed with:** ollama (mistral)

---

 # FastAPI Configuration and Usage

FastAPI is a production-ready, standards-based framework for building APIs. It's compatible with OpenAPI and JSON Schema. FastAPI is based on Starlette for web parts and Pydantic for data parts.

## Requirements

Installation:
```bash
pip install "fastapi[standard]"
```

## Example

Create a file `main.py` with the following content:

```python
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

Or use `async def` if your code uses async/await:

```python
from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

## Run the server

```bash
fastapi dev main.py
```

The command `fastapi dev` starts a server using Uvicorn with auto-reload enabled for local development. Read more about it in the FastAPI CLI docs.