import leafmap
import os
import uuid
from typing import Dict, Any
import ee
from datetime import datetime


class LeafmapService:
    """Service for generating Leafmap visualizations"""
    
    def __init__(self):
        self.static_dir = "static/images"
        os.makedirs(self.static_dir, exist_ok=True)
    
    def create_environmental_map(self, region: str, start_date: str, end_date: str, 
                                indicators: list, stats: Dict[str, Any]) -> str:
        """
        Create a Leafmap visualization for environmental analysis
        """
        try:
            # Create a new map
            m = leafmap.Map()
            
            # Get region geometry
            if region.lower() == "amazon":
                geometry = ee.Geometry.Rectangle([-80, -20, -44, 12])
            elif region.lower() == "michigan":
                geometry = ee.Geometry.Rectangle([-90.4, 41.7, -82.1, 48.2])
            elif region.lower() == "upper peninsula":
                geometry = ee.Geometry.Rectangle([-90.4, 45.1, -83.6, 48.2])
            else:
                geometry = ee.Geometry.Rectangle([-90.4, 41.7, -82.1, 48.2])
            
            # Add base map
            m.add_basemap("SATELLITE")
            
            # Add region boundary
            m.add_ee_layer(geometry, {"color": "red", "width": 2}, "Analysis Region")
            
            # Add data layers based on indicators
            if "deforestation" in indicators:
                self._add_deforestation_layer(m, geometry, start_date, end_date)
            
            if "biodiversity" in indicators:
                self._add_biodiversity_layer(m, geometry, start_date, end_date)
            
            if "wildfire" in indicators:
                self._add_wildfire_layer(m, geometry, start_date, end_date)
            
            # Add statistics as text overlay
            self._add_stats_overlay(m, stats)
            
            # Generate unique filename
            filename = f"analysis_{uuid.uuid4()}.png"
            filepath = os.path.join(self.static_dir, filename)
            
            # Save map as PNG
            m.to_image(filename=filepath, width=1200, height=800)
            
            return f"/static/images/{filename}"
            
        except Exception as e:
            print(f"Leafmap visualization error: {e}")
            # Return a placeholder image path
            return "/static/images/placeholder.png"
    
    def _add_deforestation_layer(self, m, geometry, start_date, end_date):
        """Add deforestation visualization layer"""
        try:
            # Load Landsat data for NDVI
            landsat = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry) \
                .filter(ee.Filter.lt('CLOUD_COVER', 20))
            
            # Calculate NDVI
            ndvi = landsat.select(['B5', 'B4']).mean().normalizedDifference(['B5', 'B4'])
            
            # Add NDVI layer
            m.add_ee_layer(
                ndvi, 
                {"min": -1, "max": 1, "palette": ["red", "yellow", "green"]}, 
                "Vegetation Index (NDVI)"
            )
        except Exception as e:
            print(f"Error adding deforestation layer: {e}")
    
    def _add_biodiversity_layer(self, m, geometry, start_date, end_date):
        """Add biodiversity visualization layer"""
        try:
            # Load MODIS EVI data
            modis = ee.ImageCollection('MODIS/006/MOD13Q1') \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry)
            
            evi = modis.select('EVI').mean()
            
            # Add EVI layer
            m.add_ee_layer(
                evi,
                {"min": 0, "max": 1, "palette": ["brown", "yellow", "green"]},
                "Biodiversity Index (EVI)"
            )
        except Exception as e:
            print(f"Error adding biodiversity layer: {e}")
    
    def _add_wildfire_layer(self, m, geometry, start_date, end_date):
        """Add wildfire visualization layer"""
        try:
            # Load MODIS fire data
            fire_data = ee.ImageCollection('MODIS/006/MOD14A1') \
                .filterDate(start_date, end_date) \
                .filterBounds(geometry)
            
            fire_mask = fire_data.select('FireMask').max()
            
            # Add fire layer
            m.add_ee_layer(
                fire_mask,
                {"min": 0, "max": 9, "palette": ["black", "red", "orange", "yellow"]},
                "Fire Hotspots"
            )
        except Exception as e:
            print(f"Error adding wildfire layer: {e}")
    
    def _add_stats_overlay(self, m, stats):
        """Add statistics as text overlay"""
        try:
            stats_text = "Environmental Analysis Results:\n"
            
            if stats.get("deforestation_rate") is not None:
                stats_text += f"Deforestation Rate: {stats['deforestation_rate']}%\n"
            
            if stats.get("biodiversity_index") is not None:
                stats_text += f"Biodiversity Index: {stats['biodiversity_index']}\n"
            
            if stats.get("wildfire_count") is not None:
                stats_text += f"Wildfire Count: {stats['wildfire_count']}\n"
            
            # Add text to map (this would need to be implemented based on leafmap capabilities)
            print(f"Stats overlay: {stats_text}")
            
        except Exception as e:
            print(f"Error adding stats overlay: {e}")
