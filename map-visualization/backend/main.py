from fastapi import FastAPI
from fastapi.responses import JSONResponse
import leafmap.foliumap as leafmap
import folium
import os
from datetime import datetime
import pydeck as pdk
import random

app = FastAPI(title="Enviducate")

@app.get("/")
async def health_check():
    return {"status": "API is working", "timestamp": datetime.now()}

@app.get("/generate-ann-arbor-map")
async def generate_ann_arbor_map():
    try:
        # Ann Arbor coordinates: 42.2808, -83.7430
        # Create a leafmap instance
        m = leafmap.Map(center=[42.2808, -83.7430], zoom=12)

        # Add some mock deforestation points
        deforestation_points = [
            [42.2900, -83.7500, "High Loss"],
            [42.2700, -83.7300, "Medium Loss"],
            [42.2950, -83.7200, "Low Loss"]
        ]

        # Add markers for deforestation areas
        for point in deforestation_points:
            lat, lon, severity = point
            color = "red" if "High" in severity else "orange" if "Medium" in severity else "yellow"
            m.add_marker([lat, lon], popup=f"Deforestation: {severity}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ann_arbor_deforestation_{timestamp}.html"
        filepath = f"static/{filename}"

        m.to_html(filepath)

        return JSONResponse({
              "status": "success",
              "message": "Ann Arbor deforestation map generated",
              "file_path": filepath,
              "coordinates": {"lat": 42.2808, "lon": -83.7430},
              "deforestation_points": len(deforestation_points)
        })

    except Exception as e:
         return JSONResponse({
              "status": "error",
              "message": str(e)
          }, status_code=500)
    

@app.get("/generate-ann-arbor-3d-map")
async def generate_ann_arbor_3d_map():
    try:
        # Create a leafmap with 3D terrain support
        m = leafmap.Map(
            center=[42.2808, -83.7430],
            zoom=14,
            basemap="OpenTopoMap"  # Topographic map shows elevation better
        )

        # Add terrain layer for 3D visualization
        m.add_basemap("Esri.WorldImagery")  # Satellite view as base

        # Create deforestation data with elevation simulation
        deforestation_points = [
            {"lat": 42.2900, "lon": -83.7500, "severity": "High Loss", "elevation": 280},
            {"lat": 42.2700, "lon": -83.7300, "severity": "Medium Loss", "elevation": 260},
            {"lat": 42.2950, "lon": -83.7200, "severity": "Low Loss", "elevation": 290}
        ]

        # Add markers with popup info including elevation
        for point in deforestation_points:
            color = "red" if "High" in point["severity"] else "orange" if "Medium" in point["severity"] else "yellow"
            popup_text = f"""
            <b>Deforestation Area</b><br>
            Severity: {point['severity']}<br>
            Elevation: {point['elevation']}m<br>
            Coordinates: {point['lat']:.4f}, {point['lon']:.4f}
            """

            m.add_marker(
                [point["lat"], point["lon"]],
                popup=popup_text,
                icon=folium.Icon(color=color, icon='tree')
            )

        # Add contour lines to show elevation
        m.add_layer_control()

        # Save the map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ann_arbor_3d_deforestation_{timestamp}.html"
        filepath = f"static/{filename}"

        m.to_html(filepath)

        return JSONResponse({
            "status": "success",
            "message": "3D Ann Arbor deforestation map with elevation data generated",
            "file_path": filepath,
            "coordinates": {"lat": 42.2808, "lon": -83.7430},
            "basemap": "Satellite with topographic overlay",
            "deforestation_points": len(deforestation_points)
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)
    
@app.get("/generate-ann-arbor-true-3d")
async def generate_ann_arbor_true_3d():
    try:

        # 3D deforestation data with actual height
        data = [
            {"lat": 42.2900, "lon": -83.7500, "elevation": 500, "severity": "High Loss", "color": [255, 0, 0, 160]},
            {"lat": 42.2700, "lon": -83.7300, "elevation": 300, "severity": "Medium Loss", "color": [255, 136, 0, 160]},
            {"lat": 42.2950, "lon": -83.7200, "elevation": 150, "severity": "Low Loss", "color": [255, 255, 0, 160]}
        ]     

        # Create 3D column chart
        layer = pdk.Layer(
            "ColumnLayer",
            data,
            get_position=["lon", "lat"],
            get_elevation="elevation",
            elevation_scale=10,
            get_fill_color="color",
            radius=100,
            pickable=True
        )

        # Set the viewport location
        view_state = pdk.ViewState(
            latitude=42.2808,
            longitude=-83.7430,
            zoom=13,
            pitch=45,  # Tilt for 3D effect
            bearing=0
        )

        # Render
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Severity: {severity}\nElevation: {elevation}m"}
        )

        # Save as HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ann_arbor_true_3d_{timestamp}.html"
        filepath = f"static/{filename}"

        deck.to_html(filepath)

        return JSONResponse({
            "status": "success",
            "message": "True 3D Ann Arbor deforestation visualization generated",
            "file_path": filepath,
            "view_settings": {"pitch": 45, "bearing": 0, "zoom": 13},
            "3d_columns": len(data)
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)
    
@app.get("/generate-ann-arbor-terrain-3d")
async def generate_ann_arbor_terrain_3d():
    try:
        # Create terrain layer with actual elevation data
        terrain_layer = pdk.Layer(
            "TerrainLayer",
            data=None,
            elevation_data="https://raw.githubusercontent.com/visgl/deck.gl-data/master/terrain.png",
            bounds=[-83.8, 42.2, -83.6, 42.4],  # Ann Arbor bounding box
            elevation_scale=50,
            texture="https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/terrain-mask.png"
        )

        # Add deforestation markers on top of terrain
        marker_data = [
            {"lat": 42.2900, "lon": -83.7500, "size": 150, "color": [255, 0, 0, 200], "severity": "High Loss"},
            {"lat": 42.2700, "lon": -83.7300, "size": 120, "color": [255, 136, 0, 200], "severity": "Medium Loss"},
            {"lat": 42.2950, "lon": -83.7200, "size": 80, "color": [255, 255, 0, 200], "severity": "Low Loss"}
        ]

        marker_layer = pdk.Layer(
            "ScatterplotLayer",
            marker_data,
            get_position=["lon", "lat"],
            get_radius="size",
            get_fill_color="color",
            pickable=True,
            stroked=True,
            get_line_color=[0, 0, 0],
            line_width_min_pixels=2
        )

        # 3D view settings for terrain
        view_state = pdk.ViewState(
            latitude=42.2808,
            longitude=-83.7430,
            zoom=12,
            pitch=60,  # High pitch to see terrain elevation
            bearing=30  # Rotate for better angle
        )

        deck = pdk.Deck(
            layers=[terrain_layer, marker_layer],
            initial_view_state=view_state,
            tooltip={"text": "Deforestation: {severity}"}
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ann_arbor_terrain_3d_{timestamp}.html"
        filepath = f"static/{filename}"

        deck.to_html(filepath)

        return JSONResponse({
            "status": "success",
            "message": "Terrain-based 3D Ann Arbor visualization generated",
            "file_path": filepath,
            "view_settings": {"pitch": 60, "bearing": 30, "zoom": 12},
            "layers": ["terrain", "deforestation_markers"]
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/generate-michigan-gee-fixed")
async def generate_michigan_gee_fixed():
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
        lossyear = gfc.select('lossyear').selfMask()  # CRITICAL: Add selfMask()

        # Lower tree cover threshold and test broader time range
        forest_cover = treecover2000.gte(25)  # Lowered from 50% to 25%
        forest_loss_filtered = lossyear.gte(10).And(lossyear.lte(24))  # 2010-2024

        # Combine masks
        deforestation = forest_loss_filtered.And(forest_cover).selfMask()

        # Improved sampling parameters
        deforestation_points = deforestation.sample(
            region=michigan_forests,
            scale=30,  # Native resolution instead of 100m
            numPixels=5000,  # Increased from 500
            seed=42,
            geometries=True
        )

        # Get info and check if we have data
        features = deforestation_points.getInfo()['features']
        print(f"Raw features found: {len(features)}")

        # Process data
        data_points = []
        for feature in features:
            props = feature.get('properties', {})
            lossyear_val = props.get('lossyear', 0)

            if lossyear_val > 0:  # Valid loss year
                coords = feature['geometry']['coordinates']
                loss_year = 2000 + lossyear_val
                elevation = (loss_year - 2010) * 50 + 200

                if loss_year >= 2020:
                    color = [255, 0, 0, 180]
                elif loss_year >= 2015:
                    color = [255, 136, 0, 180]
                else:
                    color = [255, 255, 0, 180]

                data_points.append({
                    "lat": coords[1],
                    "lon": coords[0],
                    "elevation": elevation,
                    "loss_year": loss_year,
                    "color": color
                })

        # Rest of visualization code unchanged...
        if data_points:
            layer = pdk.Layer(
                "ColumnLayer",
                data_points,
                get_position=["lon", "lat"],
                get_elevation="elevation",
                elevation_scale=3,
                get_fill_color="color",
                radius=150,
                pickable=True
            )

            view_state = pdk.ViewState(
                latitude=46.0,
                longitude=-87.0,
                zoom=8,
                pitch=45,
                bearing=0
            )

            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "Forest Loss Year: {loss_year}"}
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"michigan_gee_fixed_{timestamp}.html"
            filepath = f"static/{filename}"

            deck.to_html(filepath)

            return JSONResponse({
                "status": "success",
                "message": f"Michigan forest loss data found: {len(data_points)} points",
                "file_path": filepath,
                "data_points": len(data_points),
                "improvements": ["latest_dataset", "proper_masking", "native_resolution", "lower_threshold",
"extended_timerange"]
            })
        else:
            return JSONResponse({
                "status": "debug",
                "message": f"Processed {len(features)} features, {len(data_points)} valid points",
                "raw_features": len(features)
            })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"GEE Error: {str(e)}"
        }, status_code=500)

@app.get("/generate-michigan-gee-debug")
async def generate_michigan_gee_debug():
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
        forest_loss_filtered = lossyear.gte(10).And(lossyear.lte(24))

        # Combine masks
        deforestation = forest_loss_filtered.And(forest_cover).selfMask()

        # Improved sampling parameters
        deforestation_points = deforestation.sample(
            region=michigan_forests,
            scale=30,
            numPixels=5000,
            seed=42,
            geometries=True
        )

        # Get info and check if we have data
        features = deforestation_points.getInfo()['features']

        # Process data with debugging
        data_points = []
        lat_bounds = {"min": 90, "max": -90}
        lon_bounds = {"min": 180, "max": -180}

        for feature in features:
            props = feature.get('properties', {})
            lossyear_val = props.get('lossyear', 0)

            if lossyear_val > 0:
                coords = feature['geometry']['coordinates']
                lat, lon = coords[1], coords[0]

                # Track bounds for debugging
                lat_bounds["min"] = min(lat_bounds["min"], lat)
                lat_bounds["max"] = max(lat_bounds["max"], lat)
                lon_bounds["min"] = min(lon_bounds["min"], lon)
                lon_bounds["max"] = max(lon_bounds["max"], lon)

                loss_year = 2000 + lossyear_val
                # Make columns much taller and more visible
                elevation = (loss_year - 2010) * 200 + 500  # Much higher

                if loss_year >= 2020:
                    color = [255, 0, 0, 255]  # Fully opaque red
                elif loss_year >= 2015:
                    color = [255, 136, 0, 255]  # Fully opaque orange
                else:
                    color = [255, 255, 0, 255]  # Fully opaque yellow

                data_points.append({
                    "lat": lat,
                    "lon": lon,
                    "elevation": elevation,
                    "loss_year": loss_year,
                    "color": color
                })

        if data_points:
            # Create multiple layers for better visibility
            column_layer = pdk.Layer(
                "ColumnLayer",
                data_points,
                get_position=["lon", "lat"],
                get_elevation="elevation",
                elevation_scale=5,  # Higher scale
                get_fill_color="color",
                radius=300,  # Larger radius
                pickable=True,
                auto_highlight=True
            )

            # Add scatter layer as backup
            scatter_layer = pdk.Layer(
                "ScatterplotLayer",
                data_points,
                get_position=["lon", "lat"],
                get_radius=500,  # Large visible circles
                get_fill_color="color",
                pickable=True
            )

            # Calculate center from actual data bounds
            center_lat = (lat_bounds["min"] + lat_bounds["max"]) / 2
            center_lon = (lon_bounds["min"] + lon_bounds["max"]) / 2

            view_state = pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=7,  # Zoom out to see more area
                pitch=60,  # Good 3D angle
                bearing=0
            )

            deck = pdk.Deck(
                layers=[column_layer, scatter_layer],  # Both layers
                initial_view_state=view_state,
                tooltip={"text": "Forest Loss Year: {loss_year}\nElevation: {elevation}m"},
                map_style="mapbox://styles/mapbox/satellite-v9"  # Satellite background
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"michigan_gee_debug_{timestamp}.html"
            filepath = f"static/{filename}"

            deck.to_html(filepath)

            return JSONResponse({
                "status": "success",
                "message": f"Michigan forest loss visualization with {len(data_points)} points",
                "file_path": filepath,
                "data_points": len(data_points),
                "bounds": {
                    "lat_range": f"{lat_bounds['min']:.3f} to {lat_bounds['max']:.3f}",
                    "lon_range": f"{lon_bounds['min']:.3f} to {lon_bounds['max']:.3f}"
                },
                "center": {"lat": center_lat, "lon": center_lon},
                "improvements": ["dual_layers", "larger_radius", "satellite_background", "data_bounds_centering"]
            })
        else:
            return JSONResponse({
                "status": "debug",
                "message": f"No valid data points from {len(features)} features"
            })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"GEE Error: {str(e)}"
        }, status_code=500)
#Good
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