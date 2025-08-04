# fastapi Documentation - Chunk 8

**Original File:** fastapi_hybrid_002_sub_01.md

**Processed with:** ollama (mistral)

---

 FastAPI Hybrid 002 Sub-01 is a framework created by Kevin Glisson, Marc Vilanova, and Forest Monsen at Netflix. It's praised for its solid and polished structure, with Brian Okken (Python Bytes podcast host) expressing his excitement about it. Timothy Crosley, the creator of Hug, also finds it inspiring.

To use FastAPI Hybrid 002 Sub-01, you can install it via pip:

```bash
pip install fastapi_hybrid_002_sub_01
```

Here's an example of a simple FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

Errors are handled with FastAPI's built-in error handling mechanism. For example, a custom exception can be raised and caught:

```python
class MyException(Exception):
    pass

@app.get("/raise")
def raise_exception():
    raise MyException("This is a custom exception")
```

In this case, FastAPI will return a JSON response with the error details:

```json
{
  "detail": [
    {
      "loc": [
        "raise"
      ],
      "msg": "This is a custom exception",
      "type": "fastapi.exceptions.RequestValidationError",
      "value": MyException("This is a custom exception")
    }
  ]
}
```