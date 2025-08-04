# fastapi Documentation - Chunk 10

**Original File:** fastapi_hybrid_004.md

**Processed with:** ollama (mistral)

---

 Here is a summary of the FastAPI documentation for `fastapi_hybrid_004`:

**Endpoint:** `/{item_id}`

The endpoint takes an integer as the path parameter `item_id` and an optional query parameter `q` of type string.

**Usage:**

To run the server, use the command `fastapi dev main.py`. This will start a development server with auto-reload enabled using Uvicorn. The API documentation can be accessed at http://127.0.0.1:8000/docs and http://127.0.0.1:8000/redoc.

**Example:**

You can access the JSON response for `item_id=5` and optional query parameter `q=somequery` at http://127.0.0.1:8000/items/5?q=somequery.

**Errors:**

Not specified in this particular example.

**Code Example:**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

**Configuration Details:**

This example does not include specific configuration details. The general configuration for FastAPI can be found in the FastAPI documentation (<https://fastapi.tiangolo.com>).