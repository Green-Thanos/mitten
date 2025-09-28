# Mitten - Environmental Education Platform

A comprehensive environmental education platform combining real-time environmental analysis for Michigan using Google Earth Engine and Gemini AI with a modern Next.js frontend.

## 🌍 Project Overview

Mitten is an environmental education platform that provides real-time environmental analysis for Michigan using Google Earth Engine and Gemini AI integration. The platform consists of a FastAPI backend for data processing and a Next.js frontend for user interaction.

## 🏗️ Architecture

```
mitten/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API endpoints
│   │   ├── core/              # Configuration
│   │   ├── models/            # Data models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── main.py                # Application entry point
│   └── requirements.txt       # Dependencies
└── frontend/                  # Next.js frontend
    ├── src/
    │   ├── app/               # Next.js app directory
    │   ├── server/            # tRPC server setup
    │   └── trpc/              # tRPC client setup
    └── package.json           # Frontend dependencies
```

## 🚀 Quick Start

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
uv sync

# Set up Google Earth Engine
earthengine authenticate
earthengine set_project YOUR_PROJECT_ID

# Start server
uv run python main.py

# Test API
./test_enviducate.sh
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## 📋 Backend API

### Health Check

- `GET /health` - API health status

### Main Query

- `POST /api/v1/query` - Process environmental queries about Michigan

### Request Format

```json
{
  "query": "Biodiversity in Michigan wetlands",
  "visualizationType": "heatmap"
}
```

### Response Format

```json
{
  "summary": {
    "text": "Environmental analysis...",
    "stats": {
      "area_affected": 250493.0,
      "species_count": 72,
      "risk_level": "Medium"
    },
    "sources": ["Michigan DNR", "Google Earth Engine"]
  },
  "visualization": {
    "url": "/static/images/michigan_heatmap_abc123.png",
    "type": "heatmap",
    "legend": {"blue": "Low Impact", "red": "High Impact"}
  },
  "resources": {
    "charities": [...],
    "shareableUrl": "https://enviducate.com/share/abc12345"
  }
}
```

## 🔧 Key Features

### Backend Features

- **Real Data**: Google Earth Engine with Michigan bounding box `[-90, 41, -82, 48]`
- **AI Integration**: Gemini AI with Google Search for context
- **Visualizations**: Leafmap-generated images focused on Michigan
- **Caching**: Query caching for performance optimization
- **Three-Column Response**: Summary, visualization, and resources

### Frontend Features

- **Modern UI**: Built with Next.js 14 and Tailwind CSS
- **Type Safety**: Full TypeScript support with tRPC
- **Authentication**: NextAuth.js integration
- **Database**: Prisma ORM with PostgreSQL
- **Real-time**: tRPC for type-safe API calls

## 🎨 Supported Visualization Types

| Type         | Description                    | Base Map  | Use Case              |
| ------------ | ------------------------------ | --------- | --------------------- |
| `heatmap`    | Environmental impact intensity | Satellite | General analysis      |
| `choropleth` | Regional data visualization    | Satellite | Geographic comparison |
| `satellite`  | Raw satellite imagery          | Satellite | High-resolution view  |
| `terrain`    | Topographic features           | Terrain   | Geographic analysis   |
| `hybrid`     | Satellite + labels             | Hybrid    | Detailed mapping      |

## 🌍 Michigan Focus

All analysis is constrained to Michigan's bounding box `[-90, 41, -82, 48]` covering 250,493 km² of the state. The API provides:

- Real satellite data from Landsat and MODIS
- Environmental indicators (deforestation, biodiversity, wildfire, wetlands, water quality, air quality)
- Michigan-specific organizations and resources
- Educational content tailored for Michigan students

## 🔧 Configuration

### Environment Variables

#### Backend

```bash
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_SEARCH_API_KEY=your-search-key
GOOGLE_SEARCH_ENGINE_ID=your-engine-id
```

#### Frontend

```bash
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
DATABASE_URL=your-database-url
```

### Google Earth Engine Setup

```bash
# Install and authenticate
pip install earthengine-api
earthengine authenticate
earthengine set_project YOUR_PROJECT_ID
```

## 📊 Data Sources

| Dataset                    | Resolution | Use Case            | Time Range   |
| -------------------------- | ---------- | ------------------- | ------------ |
| **LANDSAT/LC08/C01/T1_SR** | 30m        | Deforestation, NDVI | 2013-present |
| **MODIS/006/MOD13Q1**      | 250m       | Biodiversity, EVI   | 2000-present |
| **MODIS/006/MOD14A1**      | 1000m      | Wildfire detection  | 2000-present |
| **COPERNICUS/S2_SR**       | 10m        | High-res analysis   | 2015-present |

## 🚀 Usage Examples

### Biodiversity Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Biodiversity in Michigan wetlands",
    "visualizationType": "heatmap"
  }'
```

### Deforestation Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Forest loss in Upper Peninsula",
    "visualizationType": "choropleth"
  }'
```

### Wildfire Risk Assessment

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Wildfire risk in Michigan forests",
    "visualizationType": "satellite"
  }'
```

## 📚 Documentation

- **Backend Swagger UI**: http://localhost:8000/docs
- **Backend ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3000

## 🛠️ Troubleshooting

### Google Earth Engine Issues

#### Error: "No project found"

```bash
earthengine set_project YOUR_PROJECT_ID
```

#### Error: "Permission denied"

1. Ensure Earth Engine API is enabled in your project
2. Check that your account has the necessary permissions
3. Wait a few minutes for permissions to propagate

#### Error: "Authentication failed"

```bash
earthengine authenticate
# Follow the browser authentication flow
```

## 🎯 Environmental Indicators

- **Deforestation**: Landsat NDVI analysis
- **Biodiversity**: MODIS EVI analysis
- **Wildfire**: MODIS fire detection
- **Wetlands**: Landsat water body analysis
- **Water Quality**: Landsat band ratio analysis
- **Air Quality**: MODIS aerosol data

## 🔄 API Endpoints

### Analysis Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/analyze-environment/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me deforestation trends in Michigan",
    "region": "michigan",
    "time_range": {
      "start": "2020-01-01",
      "end": "2024-01-01"
    }
  }'
```

### Supported Regions

- `michigan` - Michigan state
- `upper peninsula` - Upper Peninsula of Michigan
- `lower peninsula` - Lower Peninsula of Michigan
- `detroit` - Detroit metropolitan area
- `grand rapids` - Grand Rapids area

## 🚀 Deployment

The platform is designed for deployment on Vercel with Next.js frontend integration. All responses are optimized for the three-column frontend layout.

## 🎓 Educational Benefits

### For Students

- **Real Data**: Students work with actual satellite imagery
- **Scientific Accuracy**: Professional-grade environmental analysis
- **Global Coverage**: Analyze any region worldwide
- **Historical Perspective**: Track changes over decades

### For Development

- **No API Keys**: GEE handles authentication
- **Scalable**: Process large datasets efficiently
- **Reliable**: Google's infrastructure
- **Free**: No usage costs for educational purposes

## 🔍 Error Handling

### Validation Errors

```json
{
  "detail": "Query cannot be empty",
  "error_code": "VALIDATION_ERROR"
}
```

### Processing Errors

```json
{
  "detail": "Query processing failed: GEE not available",
  "error_code": "PROCESSING_ERROR"
}
```

## 🏗️ Frontend Stack

- [Next.js](https://nextjs.org) - React framework
- [NextAuth.js](https://next-auth.js.org) - Authentication
- [Prisma](https://prisma.io) - Database ORM
- [Drizzle](https://orm.drizzle.team) - Alternative ORM
- [Tailwind CSS](https://tailwindcss.com) - Styling
- [tRPC](https://trpc.io) - Type-safe APIs

## 📈 Performance Features

- **Query caching** for repeated requests
- **Efficient GEE processing** with Michigan constraints
- **Background processing** for heavy computations
- **CORS enabled** for frontend integration
- **TypeScript compatible** schemas

## 🎉 Getting Started

1. **Clone the repository**
2. **Set up Google Cloud project** and enable Earth Engine API
3. **Configure environment variables** for both backend and frontend
4. **Run authentication** commands for Google Earth Engine
5. **Start both servers** and test the integration
6. **Explore the environmental data** for Michigan!

Your Mitten platform now has access to the world's most comprehensive environmental dataset! 🌍✨
