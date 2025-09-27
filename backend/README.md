# Enviducate Backend API

A FastAPI-based backend for the Enviducate Sustainability Education Platform.

## Features

- FastAPI framework with automatic API documentation
- CORS support for frontend integration
- Environmental query processing endpoints
- Health check endpoints
- UUID-based request tracking
- ISO8601 timestamp formatting
- Environment-based configuration
- Modular structure for easy expansion

## Setup

### Using uv (Recommended)

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Environment setup:**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Run the development server:**

   ```bash
   uv run python main.py
   ```

   Or with uvicorn directly:

   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Using pip (Alternative)

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment setup:**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Run the development server:**

   ```bash
   python main.py
   ```

   Or with uvicorn directly:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI schema:** http://localhost:8000/openapi.json

## API Endpoints

### Health

- `GET /` - Basic health check
- `GET /health` - API health status
- `GET /api/v1/health/` - Detailed health check with ISO8601 timestamp

### Environmental Queries

- `POST /api/v1/query/` - Submit natural language environmental query

#### Query Endpoint Details

**Request Body:**

```json
{
  "query": "Show me wildfire risk in the Upper Peninsula"
}
```

**Response:**

```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "query": "Show me wildfire risk in the Upper Peninsula",
  "timestamp": "2025-01-27T16:45:00Z"
}
```

**Error Cases:**

- `400` - Missing or invalid query string

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py
│   │       │   └── query.py
│   │       └── api.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   └── schemas/
│       └── query.py
├── main.py
├── pyproject.toml
├── requirements.txt
├── env.example
└── README.md
```

## Development

The project uses a modular structure that makes it easy to add new features:

- **Models** (`app/models/`): Database models
- **Schemas** (`app/schemas/`): Pydantic models for request/response validation
- **Endpoints** (`app/api/v1/endpoints/`): API route handlers
- **Core** (`app/core/`): Configuration and shared utilities

## Enviducate-Specific Features

- **Query Validation**: Validates and normalizes natural language environmental queries
- **Request Tracking**: Each query gets a unique UUID for tracking
- **Michigan Focus**: Designed for Michigan environmental education queries
- **Downstream Ready**: Prepared for integration with Gemini, GEE, and Leafmap

## Next Steps

1. Add sophisticated query validation for Michigan environmental terms
2. Integrate with Gemini AI for query processing
3. Add Google Earth Engine (GEE) integration
4. Implement Leafmap visualization endpoints
5. Add comprehensive testing
6. Add logging and monitoring
