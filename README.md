# Task Manager API

A RESTful API for managing tasks with full CRUD operations, built with Python, FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- ✅ **Full CRUD Operations**: Create, Read, Update, and Delete tasks
- ✅ **RESTful API**: Clean and intuitive API design
- ✅ **Database Migrations**: Alembic for database version control
- ✅ **Data Validation**: Pydantic schemas for request/response validation
- ✅ **PostgreSQL**: Robust relational database
- ✅ **FastAPI**: Modern, fast, and type-safe framework
- ✅ **Auto Documentation**: Swagger UI and ReDoc
- ✅ **Best Practices**: SOLID, DRY, KISS, and Clean Code principles

## Technology Stack

- **Python 3.11+**
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration tool
- **PostgreSQL**: Database
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Project Structure

```
task-manager-api/
├── app/
│   ├── api/              # API endpoints
│   │   └── tasks.py      # Task endpoints
│   ├── core/             # Core configuration
│   │   └── config.py     # Settings management
│   ├── db/               # Database configuration
│   │   └── session.py    # Database session
│   ├── models/           # SQLAlchemy models
│   │   └── task.py       # Task model
│   ├── schemas/          # Pydantic schemas
│   │   └── task.py       # Task schemas
│   ├── services/         # Business logic
│   │   └── task_service.py
│   └── main.py           # Application entry point
├── migrations/           # Alembic migrations
├── .env.example          # Environment variables example
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/diegoferreiramoreno/task-manager-api.git
   cd task-manager-api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb taskmanager
   # Or using psql:
   psql -U postgres -c "CREATE DATABASE taskmanager;"
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Tasks
- `POST /tasks` - Create a new task
- `GET /tasks` - Get all tasks (with pagination)
- `GET /tasks/{id}` - Get a specific task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

## API Usage Examples

### Create a Task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "completed": false
  }'
```

### Get All Tasks
```bash
curl -X GET "http://localhost:8000/tasks?skip=0&limit=100"
```

### Get Task by ID
```bash
curl -X GET "http://localhost:8000/tasks/1"
```

### Update a Task
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "completed": true
  }'
```

### Delete a Task
```bash
curl -X DELETE "http://localhost:8000/tasks/1"
```

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic history
```

## Development

### Code Style

This project follows Python best practices:
- **SOLID principles**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **DRY (Don't Repeat Yourself)**: Avoid code duplication
- **KISS (Keep It Simple, Stupid)**: Simple and straightforward solutions
- **Clean Code**: Readable, maintainable, and well-documented code

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Task Manager API |
| `APP_VERSION` | Application version | 1.0.0 |
| `DEBUG` | Debug mode | false |
| `DATABASE_URL` | PostgreSQL connection URL | postgresql://postgres:postgres@localhost:5432/taskmanager |

## Error Handling

The API returns standard HTTP status codes:
- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

Diego Ferreira Moreno

## Support

For issues and questions, please open an issue on GitHub.
