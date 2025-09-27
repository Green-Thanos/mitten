# FastAPI Backend Testing Guide

This directory contains comprehensive shell scripts for testing the Enviducate FastAPI backend.

## 🚀 Quick Start

1. **Start the server:**

   ```bash
   ./start_server.sh
   ```

2. **Run all tests:**
   ```bash
   ./test_all.sh
   ```

## 📋 Test Scripts

### Core Testing Scripts

| Script             | Purpose                 | Usage                           |
| ------------------ | ----------------------- | ------------------------------- |
| `test_all.sh`      | Run all test suites     | `./test_all.sh [base_url]`      |
| `test_health.sh`   | Test health endpoints   | `./test_health.sh [base_url]`   |
| `test_query.sh`    | Test query endpoints    | `./test_query.sh [base_url]`    |
| `test_analysis.sh` | Test analysis endpoints | `./test_analysis.sh [base_url]` |

### Advanced Testing Scripts

| Script                   | Purpose              | Usage                                                    |
| ------------------------ | -------------------- | -------------------------------------------------------- |
| `test_performance.sh`    | Performance testing  | `./test_performance.sh [base_url] [concurrent_requests]` |
| `test_error_handling.sh` | Error handling tests | `./test_error_handling.sh [base_url]`                    |
| `start_server.sh`        | Start the server     | `./start_server.sh [port] [host]`                        |

## 🧪 Test Coverage

### Health Endpoints

- ✅ Basic health check (`/health`)
- ✅ Detailed health check (`/api/v1/health/`)
- ✅ Root endpoint (`/`)

### Query Endpoints

- ✅ Valid query submission
- ✅ Empty query validation
- ✅ Long query handling
- ✅ Michigan environmental queries
- ✅ Deforestation queries

### Analysis Endpoints

- ✅ Valid analysis requests
- ✅ Michigan-focused analysis
- ✅ Upper Peninsula analysis
- ✅ Invalid time range handling
- ✅ Missing field validation
- ✅ Async analysis processing

### Error Handling

- ✅ Invalid JSON parsing
- ✅ Missing Content-Type headers
- ✅ Invalid HTTP methods
- ✅ Non-existent endpoints
- ✅ Invalid date formats
- ✅ Missing required fields
- ✅ Large payload handling
- ✅ CORS preflight requests

### Performance Testing

- ✅ Concurrent request handling
- ✅ Different query lengths
- ✅ Response time measurement
- ✅ Memory usage monitoring

## 🔧 Prerequisites

### Required Tools

- `curl` - For HTTP requests
- `jq` - For JSON parsing (optional but recommended)
- `uv` or `python` - For running the server

### Install jq (if not available)

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

## 📊 Example Test Output

### Health Test

```bash
$ ./test_health.sh
Testing health endpoints at http://localhost:8000
==================================
1. Testing basic health check...
{
  "status": "healthy"
}

2. Testing detailed health check...
{
  "status": "ok",
  "timestamp": "2025-01-27T16:45:00Z"
}
```

### Query Test

```bash
$ ./test_query.sh
Testing query endpoints at http://localhost:8000
==================================
1. Testing valid query...
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "query": "Show me wildfire risk in the Upper Peninsula",
  "timestamp": "2025-01-27T16:45:00Z"
}
```

### Analysis Test

```bash
$ ./test_analysis.sh
Testing environmental analysis endpoints at http://localhost:8000
==================================================
1. Testing valid analysis request...
{
  "summary": "Analysis shows a 15.3% increase in deforestation...",
  "stats": {
    "deforestation_rate": 15.3,
    "biodiversity_index": 0.75,
    "wildfire_count": 42
  },
  "image_url": "/static/images/analysis_123e4567-e89b-12d3-a456-426614174000.png"
}
```

## 🐛 Troubleshooting

### Server Not Running

```bash
Error: Server is not running
```

**Solution:** Start the server first:

```bash
./start_server.sh
```

### JSON Parsing Errors

```bash
Failed to parse JSON
```

**Solution:** Install jq or check if the server is returning valid JSON.

### Permission Denied

```bash
Permission denied: ./test_health.sh
```

**Solution:** Make scripts executable:

```bash
chmod +x *.sh
```

### Analysis Endpoint Timeout

The analysis endpoint may take longer due to GEE and Leafmap processing. Consider using the async endpoint for production.

## 🔍 Custom Testing

### Test Specific Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/query/" \
  -H "Content-Type: application/json" \
  -d '{"query": "Your custom query here"}'
```

### Test with Different Base URL

```bash
./test_all.sh https://your-production-api.com
```

### Test Performance with More Concurrent Requests

```bash
./test_performance.sh http://localhost:8000 50
```

## 📈 Monitoring

### Check Server Status

```bash
curl -s http://localhost:8000/health | jq '.status'
```

### View API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json

### Monitor Logs

```bash
# If using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

## 🚀 CI/CD Integration

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Test FastAPI Backend
  run: |
    cd backend
    ./start_server.sh &
    sleep 10
    ./test_all.sh
    pkill -f uvicorn
```
