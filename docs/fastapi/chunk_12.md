# fastapi Documentation - Chunk 12

**Original File:** fastapi_hybrid_006.md

**Processed with:** ollama (mistral)

---

 FastAPI (version fastapi_hybrid_006) is a Python framework for building APIs that automatically converts JSON data, supports OpenAPI documentation, and offers features like interactive documentation systems, automatic client code generation, and auto-completion in editors. It includes a powerful Dependency Injection system, security and authentication features, and advanced techniques for declaring nested JSON models. FastAPI applications have high performance as per TechEmpower benchmarks.

Dependencies include Pydantic, Starlette, and additional packages like email-validator, httpx, jinja2, python-multipart, uvicorn, and fastapi-cli (which includes fastapi-cloud-cli for deployment to FastAPI Cloud). To install the standard group of optional dependencies, use `pip install "fastapi[standard]"`.

Example:

```Python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_name": item_id}  # Change this line to return "item_price" for auto-completion
```

For a more comprehensive example, refer to the Tutorial - User Guide.