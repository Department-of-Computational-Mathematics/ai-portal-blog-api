# AI Portal Blog API

Blog api developed for the AI webstie "Chapter".

Features a modern blog API built with FastAPI, MongoDB, and Pydantic.

## Project Structure

```plaintext
app/
├── api/                    # API endpoints
│   └── v1/
│       ├── api.py         # API router
│       └── endpoints/
│           └── blogs.py   # Blog endpoints
├── core/                  # Core application code
│   ├── __init__.py
│   ├── security.py       # Security utilities (Authentication)
│   └── config.py         # Application configuration
├── db/                    # Database
│   ├── __init__.py
│   └── database.py       # MongoDB connection
├── schemas/              # Pydantic models
│   ├── __init__.py
│   └── blog.py          # Blog schemas
├── services/            # Business logic
│   ├── __init__.py
│   ├── keycloak.py      # Keycloak integration
│   └── blog.py         # Blog services
├── __init__.py         # App initialization
└── main.py             # FastAPI application
```

## Setup

1. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Add the environment variables

    ```bash
    export BLOG_CLIENT_SECRET=your_client_secret_here
    export BLOG_MONGODB_DB_NAME=your_database_name_here
    export BLOG_MONGODB_URL=your_mongodb_url_here_with_credentials
    ```

4. Run the application:

    ```bash
    uvicorn app.main:app --reload
    ```

## API Documentation

Once the application is running, you can access:

- Interactive API documentation: <http://localhost:8000/docs>
- Alternative API documentation: <http://localhost:8000/redoc>

## Features

- CRUD operations for blog posts
- MongoDB integration with Motor
- Async operations
- Pydantic data validation
- Type hints
- Modular structure
- API versioning
- OpenAPI documentation
