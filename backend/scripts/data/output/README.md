# Output Directory

Processed files will be saved here in Enviducate MockData format.

## Output Structure

```
data/output/
├── Michigan_Gas_Storage_Fields_processed.json
├── Water_Bodies_Michigan_processed.json
├── Forest_Cover_Data_processed.json
├── Wildlife_Habitats_processed.json
└── processing_report.json
```

## File Format

Each processed file contains:

- **Environmental summary** with AI-generated insights
- **Coordinate data** sampled for visualization
- **Category classification** (energy, water, forest, etc.)
- **Relevant charities** for user engagement
- **Metadata** for frontend integration

## Integration

These files are ready for use with:

- Enviducate frontend visualization
- Educational content generation
- User engagement features
- Data sharing functionality

## Example Usage

```bash
# View processed files
ls -la data/output/

# Check processing report
cat data/output/processing_report.json

# Use in your application
import json
with open('data/output/Michigan_Gas_Storage_Fields_processed.json') as f:
    data = json.load(f)
```

