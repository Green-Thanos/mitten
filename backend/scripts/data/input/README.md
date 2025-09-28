# Input Directory

Place your GeoJSON files here for processing.

## Supported Formats

- `.geojson` - Standard GeoJSON files
- `.json` - JSON files with GeoJSON structure

## File Structure

```
data/input/
├── Michigan_Gas_Storage_Fields.geojson
├── Water_Bodies_Michigan.geojson
├── Forest_Cover_Data.geojson
└── Wildlife_Habitats.json
```

## Example Usage

```bash
# Copy your GeoJSON files here
cp /path/to/your/data.geojson data/input/

# Process all files
python ../geojson_processor.py data/input/ data/output/

# Process single file
python ../geojson_processor.py data/input/Michigan_Gas_Storage_Fields.geojson data/output/
```

## File Requirements

- Valid GeoJSON format
- Features with geometry (Point, Polygon, MultiPolygon)
- Properties with names/labels (optional but recommended)
- Coordinates in [longitude, latitude] format

