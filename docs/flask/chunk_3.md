# flask Documentation - Chunk 3

**Original File:** flask_hybrid_001.md

**Processed with:** ollama (mistral)

---

 # Flask Hybrid Extension Overview

This section provides details about the `flask_hybrid` extension for Flask, a popular web framework in Python.

## Installation

Install `flask_hybrid` using pip:

```bash
pip install flask-hybrid
```

## Configuration

To use `flask_hybrid`, first initialize it in your application:

```python
from flask import Flask
from flask_hybrid import Hybrid

app = Flask(__name__)
Hybrid(app)
```

## Usage

The extension provides hybrid decorators, combining Flask's routes and Blueprints. Use these decorators to define your application's routes:

```python
@app.route('/')
def home():
    return 'Welcome to my app!'

@app.route('/user/<int:id>')
def user(id):
    # Handle the user route

# Define a Blueprint
bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
def users():
    return 'List of users'

@bp.route('/<string:username>')
def user_by_name(username):
    # Handle the user by name route

# Register the Blueprint with the application
app.register_blueprint(bp)
```

## Errors

Handle errors using the `errorhandler` decorator or overriding the default error handlers:

```python
@app.errorhandler(Exception)
def handle_exception(err):
    return 'An error occurred.', 500
```

## Examples

You can find examples of using `flask_hybrid` in the extension's documentation, which is generated from the source code. Visit the [Issue Tracker](URL) for more information.

---
Copyright 2010 Pallets. Created using Sphinx 8.2.3.