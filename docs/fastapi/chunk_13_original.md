# fastapi Documentation - Chunk 13 (Original)

**Original File:** fastapi_hybrid_007.md

---

# fastapi_hybrid_007

**Metadata:** {'strategy': 'hybrid', 'header_level': 3, 'line_count': 29, 'document_id': 'fastapi'}

**Tokens:** 10169-10492

---

 that loads and serves your application. This includes `uvicorn[standard]`, which includes some dependencies (e.g. `uvloop`) needed for high performance serving.
* `fastapi-cli[standard]` - to provide the `fastapi` command.
    * This includes `fastapi-cloud-cli`, which allows you to deploy your FastAPI application to <a href="https://fastapicloud.com" class="external-link" target="_blank">FastAPI Cloud</a>.


### Without `standard` Dependencies

If you don't want to include the `standard` optional dependencies, you can install with `pip install fastapi` instead of `pip install "fastapi[standard]"`.

### Without `fastapi-cloud-cli`

If you want to install FastAPI with the standard dependencies but without the `fastapi-cloud-cli`, you can install with `pip install "fastapi[standard-no-fastapi-cloud-cli]"`.

### Additional Optional Dependencies

There are some additional dependencies you might want to install.

Additional optional Pydantic dependencies:

* <a href="https://docs.pydantic.dev/latest/usage/pydantic_settings/" target="_blank"><code>pydantic-settings</code></a> - for settings management.
* <a href="https://docs.pydantic.dev/latest/usage/types/extra_types/extra_types/" target="_blank"><code>pydantic-extra-types</code></a> - for extra types to be used with Pydantic.

Additional optional FastAPI dependencies:

* <a href="https://github.com/ijl/orjson" target="_blank"><code>orjson</code></a> - Required if you want to use `ORJSONResponse`.
* <a href="https://github.com/esnme/ultrajson" target="_blank"><code>ujson</code></a> - Required if you want to use `UJSONResponse`.

## License

This project is licensed under the terms of the MIT license.


---
