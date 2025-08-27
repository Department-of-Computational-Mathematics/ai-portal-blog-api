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
│   ├── exceptions.py     # Custom exception classes for HTTP exceptions
│   ├── service_tracker.py       # Service tracking utilities
│   └── config.py         # Application configuration
├── db/                    # Database
│   ├── __init__.py
│   └── database.py       # MongoDB connection
├── schemas/              # Pydantic models
│   ├── __init__.py
│   ├── responses.py     # HTTP responses for swagger docs
│   └── blog.py          # Blog schemas
├── services/            # Business logic
│   ├── __init__.py
│   ├── keycloak.py      # Keycloak integration
│   └── blog.py         # Blog services
├── __init__.py         # App initialization
└── main.py             # FastAPI application
```

## Setup (for local development)

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

## Deploy as a service

To deploy the application as a service, you can use a process manager like `systemd` or `supervisord`. Here's a basic example using `systemd`:

1. Ensure the application is cloned to `/opt/`:

    Assume it is located at `/opt/ai-portal-blog-api/` after git clone.

2. Create a service file:

    ```bash
    sudo nano /etc/systemd/system/ai-blogs-be.service
    ```

3. Add the following configuration:

    ```ini
    [Unit]
    Description=AI Blog Service
    After=network.target

    [Service]
    Type=simple
    User=root
    WorkingDirectory=/opt/ai-portal-blog-api
    ExecStart=/opt/ai-portal-blog-api/venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 3003
    Environment=BLOG_MONGODB_URL=your_db_connection_string_with_creds_here
    Environment=BLOG_CLIENT_SECRET=your_client_secret_here
    Environment=BLOG_MONGODB_DB_NAME=your_database_name_here
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

4. Start and enable the service:

    ```bash
    sudo systemctl start ai-blogs-be
    sudo systemctl enable ai-blogs-be
    ```

5. Restart the service:

    ```bash
    sudo systemctl restart ai-blogs-be
    ```

6. Stop the service:

    ```bash
    sudo systemctl stop ai-blogs-be
    ```

7. View logs:

    ```bash
    sudo journalctl -u ai-blogs-be
    ```

8. View service status

    ```bash
    sudo systemctl status ai-blogs-be
    ```

9. View all running services

    ```bash
    sudo systemctl list-units --type=service --state=running
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
