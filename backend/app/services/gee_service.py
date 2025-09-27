import ee
import pandas as pd
from typing import Dict, Any, List
import os
from datetime import datetime, timedelta


class GoogleEarthEngineService:
    """Service for interacting with Google Earth Engine"""
    
    def __init__(self):
        # Initialize Earth Engine
        try:
            ee.Initialize()
        except Exception as e:
            # For development, you might need to authenticate
            print(f"Earth Engine initialization failed: {e}")
            print("Please run: earthengine authenticate")
    
    def get_region_geometry(self, region: str) -> ee.Geometry:
        """
        Convert region string to Earth Engine geometry
        """
        # Handle different region formats
        if region.lower() == "amazon":
            # Amazon basin bounding box
            return ee.Geometry.Rectangle([-80, -20, -44, 12])
        elif region.lower() == "michigan":
            # Michigan state bounds
            return ee.Geometry.Rectangle([-90.4, 41.7, -82.1, 48.2])
        elif region.lower() == "upper peninsula":
            # Upper Peninsula of Michigan
            return ee.Geometry.Rectangle([-90.4, 45.1, -83.6, 48.2])
        else:
            # Default to Michigan if region not recognized
            return ee.Geometry.Rectangle([-90.4, 41.7, -82.1, 48.2])
    
    def analyze_deforestation(self, region: ee.Geometry, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Analyze deforestation using Landsat data
        """
        try:
            # Load Landsat 8 data
            landsat = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
                .filterDate(start_date, end_date) \
                .filterBounds(region) \
                .filter(ee.Filter.lt('CLOUD_COVER', 20))
            
            # Calculate NDVI (Normalized Difference Vegetation Index)
            def add_ndvi(image):
                ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')
                return image.addBands(ndvi)
            
            landsat_with_ndvi = landsat.map(add_ndvi)
            
            # Calculate mean NDVI for the region
            mean_ndvi = landsat_with_ndvi.select('NDVI').mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=30,
                maxPixels=1e9
            )
            
            ndvi_value = mean_ndvi.getInfo().get('NDVI', 0)
            
            # Estimate deforestation rate (simplified calculation)
            deforestation_rate = max(0, (0.7 - ndvi_value) * 100) if ndvi_value else None
            
            return {
                "deforestation_rate": round(deforestation_rate, 2) if deforestation_rate else None,
                "ndvi_mean": round(ndvi_value, 3) if ndvi_value else None
            }
        except Exception as e:
            print(f"Deforestation analysis error: {e}")
            return {"deforestation_rate": None, "ndvi_mean": None}
    
    def analyze_biodiversity(self, region: ee.Geometry, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Analyze biodiversity using MODIS vegetation data
        """
        try:
            # Load MODIS vegetation data
            modis = ee.ImageCollection('MODIS/006/MOD13Q1') \
                .filterDate(start_date, end_date) \
                .filterBounds(region)
            
            # Calculate EVI (Enhanced Vegetation Index) mean
            evi_mean = modis.select('EVI').mean().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=region,
                scale=250,
                maxPixels=1e9
            )
            
            evi_value = evi_mean.getInfo().get('EVI', 0)
            
            # Convert EVI to biodiversity index (0-1 scale)
            biodiversity_index = min(1.0, max(0.0, evi_value * 2)) if evi_value else None
            
            return {
                "biodiversity_index": round(biodiversity_index, 3) if biodiversity_index else None,
                "evi_mean": round(evi_value, 3) if evi_value else None
            }
        except Exception as e:
            print(f"Biodiversity analysis error: {e}")
            return {"biodiversity_index": None, "evi_mean": None}
    
    def analyze_wildfire(self, region: ee.Geometry, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Analyze wildfire hotspots using MODIS fire data
        """
        try:
            # Load MODIS fire data
            fire_data = ee.ImageCollection('MODIS/006/MOD14A1') \
                .filterDate(start_date, end_date) \
                .filterBounds(region)
            
            # Count fire pixels
            fire_count = fire_data.select('FireMask').sum().reduceRegion(
                reducer=ee.Reducer.sum(),
                geometry=region,
                scale=1000,
                maxPixels=1e9
            )
            
            count = fire_count.getInfo().get('FireMask', 0)
            
            return {
                "wildfire_count": int(count) if count else 0
            }
        except Exception as e:
            print(f"Wildfire analysis error: {e}")
            return {"wildfire_count": None}
    
    async def process_environmental_analysis(self, region: str, start_date: str, end_date: str, indicators: List[str]) -> Dict[str, Any]:
        """
        Process environmental analysis for specified indicators
        """
        geometry = self.get_region_geometry(region)
        results = {}
        
        if "deforestation" in indicators:
            results.update(self.analyze_deforestation(geometry, start_date, end_date))
        
        if "biodiversity" in indicators:
            results.update(self.analyze_biodiversity(geometry, start_date, end_date))
        
        if "wildfire" in indicators:
            results.update(self.analyze_wildfire(geometry, start_date, end_date))
        
        return results
