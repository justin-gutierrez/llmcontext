# fastapi Documentation - Chunk 9

**Original File:** fastapi_hybrid_003.md

**Processed with:** ollama (mistral)

---

 FastAPI is a modern framework for building REST APIs that is fast, easy to use, and highly scalable. It has been praised by developers such as Timothy Crosley (Hug creator), Ines Montani and Matthew Honnibal (Explosion AI founders and spaCy creators), and Deon Pillsbury from Cisco.

FastAPI is inspired by Hug, and it's designed to be beautifully simple yet powerful. If you are building Command Line Interface (CLI) apps instead of web APIs, you may want to check out Typer, which is FastAPI's little sibling intended to be the FastAPI of CLIs.

To install FastAPI, create a virtual environment and then run `pip install "fastapi[standard]"`. The example below demonstrates how to create an API with FastAPI:

```Python
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

Make sure to use `async def` if your code uses `async`/`await`. For more information about async and await in FastAPI, refer to the [FastAPI documentation](https://fastapi.tiangolo.com/async/#in-a-hurry).