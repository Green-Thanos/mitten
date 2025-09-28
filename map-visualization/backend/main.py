from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import leafmap.foliumap as leafmap
import folium
import os
from datetime import datetime
import re
from typing import Optional, Dict, List, Tuple

app = FastAPI(title="Enviducate - NLP Environmental Visualization")

# Pydantic models for NLP requests
class NLPVisualizationRequest(BaseModel):
    query: str  # "Show me deforestation in Michigan from 2020 to 2024"
    visualization_type: Optional[str] = "2d"  # "2d", "heatmap"

class ParsedQuery(BaseModel):
    topic: str = "deforestation"  # Default to deforestation
    location: str = "michigan"
    timeframe_start: int = 17  # Default 2017 (Hansen dataset: year - 2000)
    timeframe_end: int = 24    # Default 2024
    tree_cover_threshold: int = 25

@app.get("/")
async def health_check():
    return {"status": "Enviducate NLP API is working", "timestamp": datetime.now()}

def parse_nlp_query(query: str) -> ParsedQuery:
    """
    Parse natural language queries into structured parameters
    Examples:
    - "Show me deforestation in Michigan from 2020 to 2024"
    - "Display forest loss in Ann Arbor since 2018"
    - "What's the deforestation like in upper peninsula?"
    """
    query_lower = query.lower()

    # Extract location
    location = "michigan"  # default
    if "ann arbor" in query_lower:
        location = "ann_arbor"
    elif "upper peninsula" in query_lower or "up" in query_lower:
        location = "upper_peninsula"
    elif "lower peninsula" in query_lower or "mitten" in query_lower:
        location = "lower_peninsula"
    elif "detroit" in query_lower:
        location = "detroit"

    # Extract timeframe
    timeframe_start = 17  # default 2017
    timeframe_end = 24    # default 2024

    # Look for year patterns
    years = re.findall(r'\b(20\d{2})\b', query)
    if len(years) >= 2:
        start_year = int(years[0])
        end_year = int(years[1])
        timeframe_start = max(1, start_year - 2000)  # Hansen dataset starts at 2001
        timeframe_end = min(24, end_year - 2000)
    elif len(years) == 1:
        year = int(years[0])
        if "since" in query_lower or "from" in query_lower:
            timeframe_start = max(1, year - 2000)
            timeframe_end = 24
        else:
            # Single year
            timeframe_start = max(1, year - 2000)
            timeframe_end = max(1, year - 2000)

    # Look for "last X years" pattern
    last_years_match = re.search(r'last\s+(\d+)\s+years?', query_lower)
    if last_years_match:
        years_back = int(last_years_match.group(1))
        timeframe_start = max(1, 24 - years_back)
        timeframe_end = 24

    # Extract tree cover threshold if mentioned
    tree_cover_threshold = 25  # default
    if "dense forest" in query_lower or "heavy forest" in query_lower:
        tree_cover_threshold = 50
    elif "sparse forest" in query_lower or "light forest" in query_lower:
        tree_cover_threshold = 10

    return ParsedQuery(
        topic="deforestation",
        location=location,
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
        tree_cover_threshold=tree_cover_threshold
    )

def get_location_bounds(location: str) -> Tuple[float, float, float, float]:
    """
    Convert location names to geographic bounds
    Returns: (west, south, east, north)
    """
    location_bounds = {
        "michigan": [-90.4, 41.6, -82.1, 48.2],
        "upper_peninsula": [-90.4, 45.0, -84.0, 47.5],
        "lower_peninsula": [-86.9, 41.6, -82.1, 45.9],
        "ann_arbor": [-83.8, 42.2, -83.6, 42.4],
        "detroit": [-83.3, 42.1, -82.9, 42.5]
    }
    return location_bounds.get(location, location_bounds["michigan"])

@app.post("/generate-nlp-visualization")
async def generate_nlp_visualization(request: NLPVisualizationRequest):
    try:
        import ee

        # Initialize Earth Engine
        ee.Initialize()

        # Parse the natural language query
        parsed = parse_nlp_query(request.query)

        # Get location bounds
        west, south, east, north = get_location_bounds(parsed.location)
        region_bounds = ee.Geometry.Rectangle([west, south, east, north])

        # Use Hansen Global Forest Change dataset
        gfc = ee.Image('UMD/hansen/global_forest_change_2024_v1_12')

        # Extract bands
        treecover2000 = gfc.select('treecover2000')
        lossyear = gfc.select('lossyear').selfMask()

        # Apply parsed parameters
        forest_cover = treecover2000.gte(parsed.tree_cover_threshold)
        forest_loss_filtered = lossyear.gte(parsed.timeframe_start).And(lossyear.lte(parsed.timeframe_end))

        # Combine masks
        deforestation = forest_loss_filtered.And(forest_cover).selfMask()

        # Sample deforestation points
        deforestation_points = deforestation.sample(
            region=region_bounds,
            scale=30,
            numPixels=3000,
            seed=42,
            geometries=True
        )

        features = deforestation_points.getInfo()['features']

        # Calculate center for map
        center_lat = (south + north) / 2
        center_lon = (west + east) / 2

        # Create leafmap visualization
        m = leafmap.Map(center=[center_lat, center_lon], zoom=8)

        # Add satellite basemap
        m.add_basemap("Esri.WorldImagery")

        # Process and add markers
        data_points = []
        for feature in features:
            props = feature.get('properties', {})
            lossyear_val = props.get('lossyear', 0)

            if lossyear_val > 0:
                coords = feature['geometry']['coordinates']
                lat, lon = coords[1], coords[0]
                loss_year = 2000 + lossyear_val

                # Determine marker color based on year
                if loss_year >= 2020:
                    color = "red"
                elif loss_year >= 2015:
                    color = "orange"
                else:
                    color = "yellow"

                # Enhanced popup with query context
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; width: 200px;">
                    <h4 style="color: #d73027; margin: 0;">🌲 Forest Loss Detected</h4>
                    <hr style="margin: 5px 0;">
                    <b>Year:</b> {loss_year}<br>
                    <b>Location:</b> {lat:.4f}°N, {abs(lon):.4f}°W<br>
                    <b>Query Region:</b> {parsed.location.replace('_', ' ').title()}<br>
                    <b>Tree Cover Threshold:</b> {parsed.tree_cover_threshold}%<br>
                    <hr style="margin: 5px 0;">
                    <small>📊 Hansen Global Forest Change 2024<br>
                    🤖 Generated from: "{request.query}"</small>
                </div>
                """

                # Add marker to map
                m.add_marker(
                    [lat, lon],
                    popup=popup_html,
                    icon=folium.Icon(color=color, icon='tree')
                )

                data_points.append({
                    "lat": lat,
                    "lon": lon,
                    "loss_year": loss_year,
                    "color": color
                })

        # Add heat map layer for density visualization
        if data_points:
            heat_data = [[point["lat"], point["lon"]] for point in data_points]
            from folium.plugins import HeatMap
            HeatMap(heat_data, radius=25, blur=15, gradient={
                0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'
            }).add_to(m)

        # Add legend with query information
        legend_html = f"""
        <div style="position: fixed;
                    top: 10px; right: 10px; width: 250px; height: 200px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:12px; padding: 10px">
        <h4>🤖 NLP Query Results</h4>
        <p><b>Query:</b> "{request.query[:40]}..."</p>
        <p><b>Region:</b> {parsed.location.replace('_', ' ').title()}</p>
        <p><b>Timeframe:</b> {2000 + parsed.timeframe_start}-{2000 + parsed.timeframe_end}</p>
        <p><b>Tree Cover:</b> ≥{parsed.tree_cover_threshold}%</p>
        <hr>
        <p><i class="fa fa-tree" style="color:red"></i> Recent (2020+)</p>
        <p><i class="fa fa-tree" style="color:orange"></i> Medium (2015-2019)</p>
        <p><i class="fa fa-tree" style="color:yellow"></i> Older (2001-2014)</p>
        </div>
        """

        # Add legend to map
        m.get_root().html.add_child(folium.Element(legend_html))

        # Add layer control
        m.add_layer_control()

        # Save the map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nlp_deforestation_{parsed.location}_{timestamp}.html"
        filepath = f"static/{filename}"

        # Ensure static directory exists
        os.makedirs("static", exist_ok=True)

        m.to_html(filepath)

        return JSONResponse({
            "status": "success",
            "message": f"NLP visualization generated with {len(data_points)} forest loss points",
            "file_path": filepath,
            "query_parsed": {
                "original_query": request.query,
                "location": parsed.location,
                "timeframe": f"{2000 + parsed.timeframe_start}-{2000 + parsed.timeframe_end}",
                "tree_cover_threshold": f"{parsed.tree_cover_threshold}%",
                "region_bounds": {"west": west, "south": south, "east": east, "north": north}
            },
            "data_points": len(data_points),
            "visualization_type": "2D Leafmap with NLP parsing",
            "features": ["satellite_basemap", "colored_markers", "heatmap_layer", "nlp_legend"]
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"NLP Visualization Error: {str(e)}",
            "query": request.query
        }, status_code=500)

# Keep the original endpoint as fallback
@app.get("/generate-michigan-gee-leafmap-2d")
async def generate_michigan_gee_leafmap_2d():
    try:
        import ee

        # Initialize Earth Engine
        ee.Initialize()

        # Use latest dataset
        gfc = ee.Image('UMD/hansen/global_forest_change_2024_v1_12')

        # Michigan Upper Peninsula with better bounds
        michigan_forests = ee.Geometry.Rectangle([-90.4, 45.0, -84.0, 47.5])

        # Extract bands properly
        treecover2000 = gfc.select('treecover2000')
        lossyear = gfc.select('lossyear').selfMask()

        # Lower tree cover threshold and test broader time range
        forest_cover = treecover2000.gte(25)
        forest_loss_filtered = lossyear.gte(1).And(lossyear.lte(24))

        # Combine masks
        deforestation = forest_loss_filtered.And(forest_cover).selfMask()

        # Get deforestation points
        deforestation_points = deforestation.sample(
            region=michigan_forests,
            scale=30,
            numPixels=5000,
            seed=42,
            geometries=True
        )

        features = deforestation_points.getInfo()['features']

        # Create leafmap 2D visualization
        m = leafmap.Map(center=[46.0, -87.0], zoom=7)

        # Add satellite basemap
        m.add_basemap("Esri.WorldImagery")

        # Process and add markers
        data_points = []
        for feature in features:
            props = feature.get('properties', {})
            lossyear_val = props.get('lossyear', 0)

            if lossyear_val > 0:
                coords = feature['geometry']['coordinates']
                lat, lon = coords[1], coords[0]
                loss_year = 2000 + lossyear_val

                # Determine marker color and size based on year
                if loss_year >= 2020:
                    color = "red"
                elif loss_year >= 2015:
                    color = "orange"
                else:
                    color = "yellow"

                # Add circle marker to map
                m.add_marker(
                    [lat, lon],
                    radius=2,
                    popup=f"<b>Forest Loss</b><br>Year: {loss_year}<br>Coordinates: {lat:.4f}, {lon:.4f}",
                    icon=folium.Icon(color=color, icon='tree')
                )

                data_points.append({
                    "lat": lat,
                    "lon": lon,
                    "loss_year": loss_year,
                    "color": color
                })

        # Add heat map layer for density visualization
        if data_points:
            heat_data = [[point["lat"], point["lon"]] for point in data_points]
            from folium.plugins import HeatMap
            HeatMap(heat_data, radius=30, blur=15, gradient={
                0.2: 'blue', 0.3: 'lime', 0.5: 'orange', 1: 'red'
            }).add_to(m)

        # Add layer control
        m.add_layer_control()

        # Save the map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"michigan_gee_leafmap_2d_{timestamp}.html"
        filepath = f"static/{filename}"

        # Ensure static directory exists
        os.makedirs("static", exist_ok=True)

        m.to_html(filepath)

        return JSONResponse({
            "status": "success",
            "message": f"2D Leafmap visualization with {len(data_points)} forest loss points",
            "file_path": filepath,
            "data_points": len(data_points),
            "visualization_type": "Leafmap 2D",
            "features": ["satellite_basemap", "colored_markers", "heatmap_layer", "popups"]
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Leafmap 2D Error: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)