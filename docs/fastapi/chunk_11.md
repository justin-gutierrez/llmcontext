# fastapi Documentation - Chunk 11

**Original File:** fastapi_hybrid_005.md

**Processed with:** ollama (mistral)

---

 # FastAPI Hybrid Example (v0.0.1)

This example demonstrates the usage of FastAPI and Pydantic for creating a simple API that accepts PUT requests with JSON body. The API also includes interactive documentation via Swagger UI and Redoc.

## Requirements
- Python 3.7+
- `fastapi`
- `pydantic`

To install the required packages, run:
```bash
pip install fastapi pydantic uvicorn
```

## Example Usage

The example below defines a FastAPI application with three endpoints (root, item, and update_item) that accept GET, PUT requests respectively. The Item class is defined using Pydantic for declaring the structure of the JSON body.

```Python
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
```

The `fastapi dev` server should automatically reload when changes are made to the code.

## Interactive API Documentation

Navigate to <http://127.0.0.1:8000/docs> for Swagger UI documentation, or <http://127.0.0.1:8000/redoc> for Redoc. The interactive API documentation will be updated automatically and allow you to directly interact with the API.

## Errors & Validation

FastAPI provides automatic validation of data and clear errors when the data is invalid, including support for deeply nested JSON objects. For example, the PUT request to `/items/{item_id}` will validate the structure of the JSON body against the Item class definition.

## Automatic Conversion

FastAPI automatically converts input data coming from the network (JSON, Path parameters, Query parameters, Cookies, Headers, Forms, Files) and output data as JSON for network communication.

## OpenAPI Support

FastAPI provides automatic OpenAPI documentation that can be used by interactive documentation systems and automatic client code generation systems for various languages.

This example only scratches the surface of what FastAPI offers. For more information, please refer to the official [FastAPI documentation](https://fastapi.tiangolo.com/).