# fastapi Documentation - Chunk 3

**Original File:** fastapi_hybrid_000_sub_02.md

**Processed with:** ollama (mistral)

---

 FastAPI documentation summary:

The `fastapi dev` command reads your main.py file, starts a server using Uvicorn with auto-reload enabled for local development. You can create an API that receives HTTP requests in the paths `/` and `/items/{item_id}` with GET operations. The path `/items/{item_id}` has an optional query parameter `q`.

For example, to receive a body from a PUT request, declare the body using standard Python types such as:

```python
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

# ... function definitions follow here
```

The interactive API documentation can be accessed at `http://127.0.0.1:8000/docs` (Swagger UI) and `http://127.0.0.1:8000/redoc` (Redoc). FastAPI automatically provides editor support, data validation, conversion of input and output data, and interactive API documentation.

For this example, FastAPI will validate the presence and type of `item_id` in the path for GET and PUT requests and check the optional query parameter `q` for GET requests. It will also read the body as JSON for PUT requests, checking for required attributes like `name`, `price`, and an optional `is_offer`. All this works for deeply nested JSON objects.