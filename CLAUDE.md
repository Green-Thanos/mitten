# CLAUDE.md - Enviducate Leafmap & MapLibre Visualization Implementation

## IMPORTANT: Claude Usage Instructions
**Claude should ONLY provide guidance and commands to run. Do NOT write code automatically unless explicitly asked to write specific code. Guide the user through the setup process step-by-step.**

## Project Context
**Enviducate**: Michigan-focused sustainability education platform using T3 stack
**Tagline**: "Envision a better environment through education"
**Scope**: Deforestation visualization for Michigan (2017-2024 timeframe)
**Timeline**: 24-hour hackathon

## Tech Stack
- **Backend**: FastAPI (Python 3.11 with uv package manager)
- **Environment**: WSL (Ubuntu 22.04)
- **Visualization**: Leafmap + MapLibre backend
- **Data Source**: Google Earth Engine (GEE) AlphaEarth embeddings
- **NLP Integration**: Gemini API for query parsing
- **Deployment**: Vercel

## Key Implementation Tasks

### Phase 1: Environment Setup (Hours 0-4)
```bash
# Setup commands to run
uv init enviducate-backend
cd enviducate-backend
uv add fastapi uvicorn leafmap folium
```

### Phase 1.5: Basic FastAPI App with Ann Arbor Test
```bash
# Create app structure
mkdir app
touch app/__init__.py
touch app/main.py
mkdir static
```

**Run the server:**
```bash
cd enviducate-backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test the endpoints:**
```bash
# Test health check
curl http://localhost:8000/

# Test Ann Arbor map generation
curl http://localhost:8000/generate-ann-arbor-map
```

**Ask Claude**: "Set up FastAPI project structure for Enviducate with Python 3.11 and uv on WSL. Include environment setup for GEE authentication, Leafmap, and MapLibre integration."

### Phase 2: Core Visualization Endpoint (Hours 4-8)
**Geographic Constraints**: Michigan bounding box `[-90, 41, -82, 48]`

**Ask Claude**: "Create FastAPI endpoint `/generate-deforestation-map` that:
1. Accepts preset parameters (topic: 'deforestation', timeframe: '2017-2024')
2. Queries GEE for AlphaEarth embeddings in Michigan bounding box
3. Generates Leafmap visualization with MapLibre backend
4. Uses red/green color scheme (red=loss, green=stable)
5. Exports as PNG and returns URL in JSON response"

### Phase 3: NLP Integration Compatibility (Hours 8-12)
**Data Structure**:
```typescript
interface VisualizationRequest {
  topic: 'deforestation';
  timeframe: '2017-2024';
  region?: 'upper-peninsula' | 'lower-peninsula';
}

interface VisualizationResponse {
  pngUrl: string;
  metadata: {
    topic: string;
    timeframe: string;
    boundingBox: number[];
  };
  error: string | null;
}
```

**Ask Claude**: "Enhance FastAPI endpoint to accept Gemini NLP JSON input with topic and timeframe validation. Include fallback handling for invalid inputs and preset value processing."

### Phase 4: MapLibre 3D Stretch Goal (Hours 16-20)
**Ask Claude**: "Implement 3D visualization using MapLibre in Leafmap for isometric/rotated deforestation maps. Export as PNG while maintaining compatibility with existing 2D endpoint."

## Critical WSL Dependencies
```bash
# Required for headless visualization
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx xvfb
```

## Common Error Handling Scenarios

### GEE Authentication Issues
**Ask Claude**: "Debug GEE OAuth authentication in WSL environment for FastAPI integration. Handle service account key setup and authentication flow."

### Leafmap PNG Export Failures
**Ask Claude**: "Troubleshoot Leafmap PNG export in headless WSL environment. Include Xvfb setup and display buffer configuration."

### MapLibre Integration Problems
**Ask Claude**: "Fix MapLibre GL JS integration with Leafmap for 3D visualization export in FastAPI backend."

## Testing & Validation

### Local Testing
**Ask Claude**: "Create FastAPI test endpoints for:
1. Mock deforestation data visualization
2. GEE connection validation
3. PNG export functionality
4. NLP input validation"

### Performance Optimization
**Ask Claude**: "Optimize FastAPI for sub-5-second deforestation map generation. Include caching strategy for preset Michigan timeframes."

## Deployment Preparation

### Vercel Configuration
**Ask Claude**: "Configure FastAPI with uv for Vercel deployment. Ensure GEE credentials, Leafmap dependencies, and MapLibre work in serverless environment."

### Environment Variables
```env
GEE_SERVICE_ACCOUNT_KEY=path/to/key.json
GEE_PROJECT_ID=your-project-id
MAPLIBRE_API_KEY=your-key
```

## Emergency Fallbacks

### Mock Data
**Ask Claude**: "Create realistic mock deforestation data for Michigan that generates convincing Leafmap visualization if GEE API fails."

### Static Fallback
**Ask Claude**: "Implement static PNG fallback system for deforestation visualization if dynamic generation fails."

## Demo Requirements
- Michigan deforestation heatmap (2017-2024)
- Red/green color coding
- PNG export under 5 seconds
- Compatible with NLP JSON input
- Error handling for API failures

## Key Prompting Tips
1. Always mention "Michigan bounding box [-90, 41, -82, 48]"
2. Specify "WSL Ubuntu 22.04 environment"
3. Include "24-hour hackathon timeline"
4. Request "NLP compatibility with Gemini JSON"
5. Emphasize "PNG export for frontend integration"

## File Structure
```
enviducate-backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── visualization/    # Leafmap + MapLibre
│   ├── gee_client/      # Earth Engine integration
│   └── models/          # Pydantic models
├── static/              # Generated PNGs
├── pyproject.toml       # uv dependencies
└── .env                 # Environment variables
```

## Lint & Type Check Commands
```bash
uv run ruff check .
uv run mypy app/
uv run pytest tests/
```

---
*Generated for Enviducate hackathon - Michigan deforestation visualization implementation*