# flask Documentation - Chunk 2

**Original File:** flask_hybrid_000_sub_01.md

**Processed with:** ollama (mistral)

---

 # Flask Hybrid Sub-Chunk 1

**Contents:**
- Explicit Application Object
- Routing System
- One Template Engine
- Thread Locals, Async/await, ASGI support
- Flask Extension Development
- Configuration Techniques
- Data During a Request
- Views and Models
- Recommended Extension Guidelines
- Contributing & License
- Project Links & Donations

**Flask Overview:**
- A micro web framework for Python, built with a small core and easy extensibility.
- Not a full-featured framework like Django, but provides essential features for building web applications.
- Supports extension development to add custom functionality.

**Key Features:**
- Explicit Application Object: The application object is created explicitly, unlike some other web frameworks where the app is implicitly defined.
- Routing System: URL routes can be registered using either class-based views or function-based views.
- One Template Engine: Flask uses Jinja2 as its default template engine, but it's easy to use others with extensions.
- Thread Locals, Async/await, ASGI support: Flask supports thread locals for per-thread state and is moving towards async/await and ASGI for improved performance in asynchronous applications.

**Flask Extension Development:**
- An extension is a package that extends the functionality of Flask.
- Extensions are registered with an application object, allowing them to add their behavior to the app.
- The extension class should be named `FlaskExtension` and initialized with the `create_app()` method.

**Configuration Techniques:**
- Configurations can be set using various methods like reading from environment variables, files, or even creating a custom config object.
- Flask provides a `Config` class to manage configurations, making it easy to access and modify them throughout the application.

**Data During a Request:**
- Data can be accessed during a request through various objects such as `request`, `g`, or `current_app`.
- The `request` object contains information about the incoming request, while `g` (short for "globals") is used for thread-local storage.

**Views and Models:**
- Views are functions or classes that handle HTTP requests and generate responses.
- Models represent the data structures of the application, usually handled by a database ORM like SQLAlchemy or Flask-SQLAlchemy.

**Recommended Extension Guidelines:**
- Follow best practices for extension development, including clear documentation, easy installation, and minimal dependencies.

**Contributing & License:**
- Contributions are welcome! Check the project links for more information on how to contribute.
- Flask is released under the BSD 3-Clause License.