# fastapi Documentation - Chunk 13

**Original File:** fastapi_hybrid_007.md

**Processed with:** ollama (mistral)

---

 FastAPI Documentation: fastapi_hybrid_007
==========================================

**Dependencies:**

- `uvicorn[standard]` for serving the application and includes dependencies like `uvloop`.
- `fastapi-cli[standard]` to provide the `fastapi` command, which includes `fastapi-cloud-cli` for deploying FastAPI applications to [FastAPI Cloud](https://fastapicloud.com).

**Installation:**

1. To install without the optional dependencies, use `pip install fastapi`.
2. To install with standard dependencies but without `fastapi-cloud-cli`, use `pip install "fastapi[standard-no-fastapi-cloud-cli]"`.

**Optional Dependencies:**

1. Additional Pydantic dependencies:
   - [pydantic-settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/) for settings management.
   - [pydantic-extra-types](https://docs.pydantic.dev/latest/usage/types/extra_types/extra_types/) for extra types to be used with Pydantic.
2. Additional FastAPI dependencies:
   - `orjson` required if you want to use `ORJSONResponse`.
   - `ujson` required if you want to use `UJSONResponse`.

**License:**

This project is licensed under the terms of the MIT license.