# GeoJSON Processing Pipeline

A comprehensive pipeline for processing GeoJSON files and generating environmental summaries using Gemini AI for the Enviducate platform.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** with required packages
2. **Node.js 16+** (for JavaScript version)
3. **Gemini API Key** (optional, fallback analysis available)

### Installation

```bash
# Install Python dependencies
cd backend
uv sync

# Install Node.js dependencies (if using JS version)
npm install
```

### Environment Setup

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key-here"
```

## 📁 Scripts Overview

### 1. `geojson_processor.py` - Main Python Processor
Full-featured processor with Gemini AI integration.

**Features:**
- ✅ Gemini AI analysis and summarization
- ✅ Coordinate extraction from all GeoJSON geometry types
- ✅ Smart sampling of coordinate points
- ✅ Category detection and charity matching
- ✅ Fallback analysis when Gemini is unavailable
- ✅ Batch processing support

**Usage:**
```bash
# Process single file
python geojson_processor.py input.geojson output_dir/

# Process directory
python geojson_processor.py input_dir/ output_dir/
```

### 2. `geojson_to_mockdata.js` - JavaScript Converter
Lightweight JavaScript version for quick conversions.

**Features:**
- ✅ Fast coordinate extraction
- ✅ Basic category detection
- ✅ MockData format output
- ✅ No external AI dependencies

**Usage:**
```bash
# Process single file
node geojson_to_mockdata.js input.geojson output.json

# Process directory
node geojson_to_mockdata.js input_dir/ output_dir/
```

### 3. `batch_process_geojson.py` - Batch Processor
Advanced batch processing with reporting.

**Features:**
- ✅ Batch processing of multiple files
- ✅ Processing reports and statistics
- ✅ Dry-run mode for testing
- ✅ File limit controls
- ✅ Error handling and recovery

**Usage:**
```bash
# Process all files in directory
python batch_process_geojson.py input_dir/ output_dir/

# Process with limits
python batch_process_geojson.py input_dir/ output_dir/ --max-files 10

# Dry run to see what would be processed
python batch_process_geojson.py input_dir/ output_dir/ --dry-run
```

## 📊 Input/Output Format

### Input: GeoJSON Files
The pipeline supports standard GeoJSON files with:
- **Point** geometries
- **Polygon** geometries  
- **MultiPolygon** geometries
- **Properties** with names/labels

### Output: Enviducate MockData Format
```json
{
  "id": "unique-id",
  "originalQuery": "Data Title",
  "category": "energy|water|forest|wildlife|air|environmental",
  "summary": "AI-generated summary of the data",
  "sources": ["Data Source 1", "Data Source 2"],
  "charities": [
    {
      "name": "Charity Name",
      "url": "https://charity-url.org",
      "description": "Charity description"
    }
  ],
  "visualizations": [
    {
      "type": "pinpoints",
      "data": [
        {"lat": 42.123, "lng": -83.456, "label": "Point Name"}
      ],
      "metadata": {
        "title": "Visualization Title",
        "description": "Description",
        "source": "Data Source",
        "lastUpdated": "2025-01-27T16:45:00Z",
        "totalPoints": 1000,
        "sampledPoints": 50
      }
    }
  ],
  "shareableUrl": "https://enviducate.org/result/abc123",
  "generatedAt": "2025-01-27T16:45:00Z",
  "insights": ["Key insight 1", "Key insight 2"],
  "concerns": ["Environmental concern 1", "Environmental concern 2"]
}
```

## 🔧 Configuration

### `config.json` - Pipeline Configuration
```json
{
  "geojson_processing": {
    "default_sample_size": 50,
    "max_sample_size": 1000,
    "supported_formats": [".geojson", ".json"],
    "gemini_enabled": true
  },
  "categories": {
    "energy": {
      "keywords": ["gas", "energy", "oil"],
      "charities": [...]
    }
  }
}
```

## 🎯 Supported Categories

The pipeline automatically detects categories based on filename and content:

| Category | Keywords | Description |
|----------|----------|-------------|
| **energy** | gas, energy, oil, fuel, power | Energy infrastructure and facilities |
| **water** | water, lake, river, stream, wetland | Water bodies and aquatic features |
| **forest** | forest, tree, wood, vegetation | Forest areas and vegetation |
| **wildlife** | wildlife, animal, bird, species | Wildlife habitats and species |
| **air** | air, pollution, quality, emission | Air quality monitoring points |
| **environmental** | environmental, monitoring, data | General environmental data |

## 📈 Processing Features

### Coordinate Extraction
- **Point geometries**: Direct coordinate extraction
- **Polygon geometries**: Extract all boundary coordinates
- **MultiPolygon geometries**: Extract coordinates from all polygons
- **Property mapping**: Use `FieldName` or `name` properties for labels

### Smart Sampling
- **Even distribution**: Sample coordinates evenly across the dataset
- **Configurable size**: Default 50 points, configurable up to 1000
- **Preserve density**: Maintain spatial distribution patterns

### AI Analysis (Gemini)
- **Title generation**: Create descriptive titles
- **Category detection**: Intelligent category classification
- **Summary generation**: Comprehensive data summaries
- **Insight extraction**: Key environmental insights
- **Concern identification**: Environmental concerns and opportunities

### Fallback Analysis
When Gemini AI is unavailable:
- **Basic categorization**: Based on filename keywords
- **Template summaries**: Standard environmental data descriptions
- **Default charities**: Category-appropriate organizations

## 🚀 Example Workflows

### 1. Process Single Gas Storage File
```bash
# Using Python processor
python geojson_processor.py Michigan_Gas_Storage_Fields.geojson output/

# Using JavaScript converter
node geojson_to_mockdata.js Michigan_Gas_Storage_Fields.geojson output/gas_storage.json
```

### 2. Batch Process Environmental Data
```bash
# Process all GeoJSON files in a directory
python batch_process_geojson.py environmental_data/ processed_data/

# With processing limits
python batch_process_geojson.py environmental_data/ processed_data/ --max-files 5
```

### 3. Test Processing (Dry Run)
```bash
# See what would be processed without actually processing
python batch_process_geojson.py environmental_data/ processed_data/ --dry-run
```

## 📊 Output Reports

### Processing Report
After batch processing, a `processing_report.json` is generated:
```json
{
  "processing_summary": {
    "total_files": 10,
    "successful_files": 8,
    "failed_files": 2,
    "timestamp": "2025-01-27T16:45:00Z"
  },
  "processed_files": [
    {
      "filename": "Gas Storage Fields",
      "category": "energy",
      "points_count": 50,
      "id": "mock_12345"
    }
  ]
}
```

## 🔍 Error Handling

### Common Issues
1. **Invalid GeoJSON**: Missing features or malformed geometry
2. **No coordinates**: Empty or invalid coordinate data
3. **Gemini API errors**: Network issues or API limits
4. **File permissions**: Read/write access problems

### Troubleshooting
- Check GeoJSON validity with online validators
- Verify file permissions and paths
- Test with small sample files first
- Check Gemini API key and quotas

## 🎯 Integration with Enviducate

The processed files are ready for integration with the Enviducate platform:

1. **Frontend visualization**: Use the `visualizations` array for map rendering
2. **Educational content**: Use `summary`, `insights`, and `concerns` for learning materials
3. **Action items**: Use `charities` for user engagement
4. **Sharing**: Use `shareableUrl` for result sharing

## 📚 Dependencies

### Python Version
- `google-generativeai` - Gemini AI integration
- `fastapi` - Web framework (for API integration)
- `pydantic` - Data validation

### JavaScript Version
- `fs` - File system operations (Node.js built-in)
- `path` - Path utilities (Node.js built-in)

## 🚀 Next Steps

1. **Set up your Gemini API key** for AI-powered analysis
2. **Prepare your GeoJSON files** in the input directory
3. **Run the batch processor** to generate MockData files
4. **Integrate with Enviducate** frontend for visualization
5. **Customize categories and charities** in `config.json`

Your GeoJSON processing pipeline is ready to transform environmental data into engaging educational content! 🌍✨

