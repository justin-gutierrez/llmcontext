# fastapi Documentation - Chunk 6

**Original File:** fastapi_hybrid_001_sub_01.md

**Processed with:** ollama (mistral)

---

 # FastAPI Configuration, Usage, Errors, and Examples

FastAPI is a modern web framework for building APIs with Python 3.7+ based on standard Python type hints.

## Installation

```bash
pip install fastapi[all]
```

## Basic Example

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

## Routing

```python
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int = Path(..., gt=0), q: str = Query(None)):
    return {"item_id": item_id, "q": q}
```

## Middleware

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Errors

Custom exceptions can be raised and caught using the `HTTPException`.

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id not in [1, 2]:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

For more detailed information and further resources, refer to the official FastAPI documentation: https://fastapi.tiangolo.com/