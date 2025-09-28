import google.generativeai as genai
import ee
import leafmap
import httpx
import json
import os
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.config import settings


class EnviducateService:
    """Unified service for Enviducate environmental analysis with real GEE data and Gemini integration"""
    
    # Michigan bounding box: [-90, 41, -82, 48]
    MICHIGAN_BBOX = [-90, 41, -82, 48]
    _michigan_geometry = None
    
    @property
    def michigan_geometry(self):
        """Get Michigan geometry, initializing GEE if needed"""
        if self._michigan_geometry is None:
            self._ensure_initialized()
            if self.gee_available:
                self._michigan_geometry = ee.Geometry.Rectangle(self.MICHIGAN_BBOX)
            else:
                # Return a mock geometry for fallback
                self._michigan_geometry = None
        return self._michigan_geometry
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.model = None
        self.gee_available = False
        self.initialized = False
        self.static_dir = "static/images"
        self.cache = {}  # Simple in-memory cache
        os.makedirs(self.static_dir, exist_ok=True)

    def _ensure_initialized(self):
        """Initialize all services when needed"""
        if self.initialized:
            return
            
        # Initialize Gemini
        if self.gemini_api_key and self.gemini_api_key.strip():
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini: {e}")
        
        # Initialize Google Earth Engine
        try:
            ee.Initialize(project='enviducate-hackathon')
            self.gee_available = True
            print("Google Earth Engine initialized successfully with project: enviducate-hackathon")
        except Exception as e:
            print(f"Earth Engine initialization failed: {e}")
            self.gee_available = False
        
        self.initialized = True

    def _get_cache_key(self, query: str, visualization_type: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(f"{query}_{visualization_type}".encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            # Check if cache is still valid (24 hours)
            if datetime.now().timestamp() - cached_data.get('timestamp', 0) < 86400:
                return cached_data.get('data')
        return None

    def _cache_result(self, cache_key: str, data: Dict[str, Any]):
        """Cache result for future use"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }

    # === GEMINI + GOOGLE SEARCH INTEGRATION ===
    
    async def process_query_with_gemini(self, query: str) -> Dict[str, Any]:
        """Process query with Gemini and Google Search for real context"""
        self._ensure_initialized()
        
        if not self.model:
            return self._get_fallback_context(query)

        try:
            # Search for recent Michigan environmental data
            search_results = await self._search_michigan_environmental_data(query)
            
            # Use Gemini to parse query and integrate search results
            search_results_str = json.dumps(search_results, indent=2)
            # Get comprehensive list of available GEE metrics
            try:
                all_metrics = GEEMetricsCatalog.get_all_metrics()
                metrics_list = []
                for metric_id, metric_info in all_metrics.items():
                    metrics_list.append(f"- {metric_id}: {metric_info['name']} ({metric_info['description']})")
                
                metrics_catalog = "\n".join(metrics_list[:50])  # Limit to first 50 for prompt size
            except Exception as e:
                print(f"Error loading metrics catalog: {e}")
                metrics_catalog = "Metrics catalog unavailable"
            
            prompt = f"""
You are an environmental data analyst focused on Michigan. Analyze the following natural language query and the associated search results.

Query: "{query}"
Search Results: {search_results_str}

Available Google Earth Engine Metrics:
{metrics_catalog}

Return a JSON object with the following fields:

1. indicators: Array of relevant environmental indicators from ["deforestation", "biodiversity", "wildfire", "wetlands", "water_quality", "air_quality"]

2. context: A single, cohesive paragraph (3-5 sentences) that synthesizes the query and search results into a human-readable summary. Use scientific terminology, focus on Michigan, highlight key trends, risks, and metrics, and make it educational.

3. sources: Array of credible sources used (Michigan DNR, NGOs, academic publications).

4. key_metrics: Array of specific GEE metric IDs that are most relevant to this query. Select from the available metrics list above. Choose 3-8 most relevant metrics.

5. relevant_metrics: Array of objects with detailed metric information for the selected key_metrics. Each object should have:
   - id: metric ID
   - name: human-readable name
   - description: what this metric measures
   - category: metric category
   - relevance_score: score from 0-1 indicating how relevant this metric is to the query

6. flags: Include if applicable:
   - "not_michigan" if the query is unrelated to Michigan
   - "not_relevant" if the query is outside the scope of analyzable environmental indicators

Requirements:
- Use Michigan-specific data wherever possible.
- Provide at least 2 sources if available.
- Keep JSON strictly valid and parsable.
- If indicators cannot be determined, return an empty array.
- Select metrics that are most relevant to the specific query and indicators.

Example output:
{{
  "indicators": ["biodiversity", "wetlands"],
  "context": "Michigan's Great Lakes wetlands support over 200 species, but urban expansion, pollution, and climate-driven changes are reducing habitat quality. These pressures threaten biodiversity and ecosystem services, highlighting the importance of conservation and restoration efforts. Monitoring wetland area and species counts can help track progress and guide environmental policy.",
  "sources": ["Michigan DNR 2025", "Great Lakes Protection Fund 2024"],
  "key_metrics": ["ndwi", "habitat_diversity", "species_richness", "wetland_area_km2"],
  "relevant_metrics": [
    {{
      "id": "ndwi",
      "name": "Normalized Difference Water Index",
      "description": "Water body detection and water content in vegetation",
      "category": "water",
      "relevance_score": 0.9
    }},
    {{
      "id": "habitat_diversity",
      "name": "Habitat Diversity Index",
      "description": "Shannon diversity index of habitat types",
      "category": "biodiversity",
      "relevance_score": 0.8
    }}
  ],
  "flags": []
}}
"""
            
            response = self.model.generate_content(prompt)
            print(f"Gemini raw response: {response.text[:200]}...")
            
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Cleaned response: {response_text[:200]}...")
                return self._get_fallback_context(query)
            
            # Integrate search results into sources
            if 'sources' not in result:
                result['sources'] = []
            
            for search_result in search_results:
                if search_result.get('source'):
                    result['sources'].append(search_result['source'])
            
            return result
            
        except Exception as e:
            print(f"Gemini query processing error: {e}")
            return self._get_fallback_context(query)

    async def _search_michigan_environmental_data(self, query: str) -> List[Dict[str, Any]]:
        """Search for recent Michigan environmental data using Google Search"""
        if not self.google_search_api_key or not self.google_search_engine_id:
            return []

        try:
            search_query = f"{query} Michigan environmental data site:michigan.gov OR site:epa.gov OR site:usgs.gov"
            
            async with httpx.AsyncClient() as client:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": self.google_search_api_key,
                    "cx": self.google_search_engine_id,
                    "q": search_query,
                    "num": 5
                }
                
                response = await client.get(url, params=params)
                data = response.json()
                
                results = []
                for item in data.get("items", []):
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", ""),
                        "source": self._extract_source_name(item.get("link", ""))
                    })
                
                return results
                
        except Exception as e:
            print(f"Google Search error: {e}")
            return []

    def _extract_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        if "michigan.gov" in url:
            return "Michigan DNR"
        elif "epa.gov" in url:
            return "US EPA"
        elif "usgs.gov" in url:
            return "USGS"
        elif "nature.org" in url:
            return "The Nature Conservancy"
        else:
            return "Environmental Research"


    def _get_fallback_context(self, query: str) -> Dict[str, Any]:
        """Fallback context when Gemini is not available"""
        return {
            "indicators": [],
            "context": f"Unable to process environmental analysis for {query} - AI services unavailable.",
            "sources": [],
            "key_metrics": [],
            "relevant_metrics": []
        }

    # === GOOGLE EARTH ENGINE ANALYSIS ===
    
    def _create_sample_points(self, num_points: int = 20) -> ee.FeatureCollection:
        """Create sample points across Michigan for analysis"""
        import random
        random.seed(42)
        
        west, south, east, north = self.MICHIGAN_BBOX
        sample_lons = [west + (east - west) * random.random() for _ in range(num_points)]
        sample_lats = [south + (north - south) * random.random() for _ in range(num_points)]
        
        return ee.FeatureCollection([
            ee.Feature(ee.Geometry.Point([lon, lat]))
            for lon, lat in zip(sample_lons, sample_lats)
        ])
    
    async def analyze_michigan_environment(self, query: str, indicators: List[str]) -> Dict[str, Any]:
        """Analyze Michigan environment using Google Earth Engine with real data"""
        self._ensure_initialized()
        
        if not self.gee_available:
            print(f"GEE not available - returning empty data for indicators: {indicators}")
            return {
                "area_affected": 250493.0,  # Michigan total area
                "data_source": "GEE not available",
                "region": "Michigan",
                "bbox": self.MICHIGAN_BBOX
            }

        try:
            results = {}
            
            # Always use Michigan bounding box
            geometry = self.michigan_geometry
            
            if "deforestation" in indicators:
                results.update(self._analyze_deforestation_michigan(geometry))
            
            if "biodiversity" in indicators:
                results.update(self._analyze_biodiversity_michigan(geometry))
            
            if "wildfire" in indicators:
                results.update(self._analyze_wildfire_michigan(geometry))
            
            if "wetlands" in indicators:
                results.update(self._analyze_wetlands_michigan(geometry))
            
            if "water_quality" in indicators:
                results.update(self._analyze_water_quality_michigan(geometry))
            
            if "air_quality" in indicators:
                results.update(self._analyze_air_quality_michigan(geometry))
            
            # Calculate area affected (Michigan area in km²)
            results["area_affected"] = 250493.0  # Michigan total area
            results["data_source"] = "Google Earth Engine"
            results["region"] = "Michigan"
            results["bbox"] = self.MICHIGAN_BBOX
            
            return results
            
        except Exception as e:
            print(f"GEE analysis error: {e}")
            return {
                "area_affected": 250493.0,  # Michigan total area
                "data_source": "GEE error",
                "region": "Michigan",
                "bbox": self.MICHIGAN_BBOX
            }

    def _analyze_deforestation_michigan(self, geometry: ee.Geometry) -> Dict[str, Any]:
        """Analyze deforestation in Michigan using sample-based approach"""
        try:
            # Use Hansen Global Forest Change dataset (pre-processed)
            hansen = ee.Image('UMD/hansen/global_forest_change_2023_v1_11')
            
            # Create sample points across Michigan
            sample_points = self._create_sample_points(20)
            
            # Get forest loss data for sample points
            forest_loss = hansen.select('loss').sampleRegions(
                collection=sample_points,
                scale=1000
            )
            
            # Calculate statistics from samples
            loss_values = forest_loss.aggregate_array('loss').getInfo()
            deforestation_rate = (sum(loss_values) / len(loss_values)) * 100 if loss_values else 0
            
            # Get NDVI from MODIS for sample points
            modis = ee.ImageCollection('MODIS/061/MOD13Q1') \
                .filterDate('2022-01-01', '2024-01-01') \
                .filterBounds(geometry) \
                .select('NDVI')
            
            ndvi_sample = modis.mean().sampleRegions(
                collection=sample_points,
                scale=1000
            )
            
            ndvi_values = ndvi_sample.aggregate_array('NDVI').getInfo()
            ndvi_mean = sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0
            
            return {
                "deforestation_rate": round(deforestation_rate, 2),
                "ndvi_mean": round(ndvi_mean, 3)
            }
        except Exception as e:
            print(f"Deforestation analysis error: {e}")
            raise e

    def _analyze_biodiversity_michigan(self, geometry: ee.Geometry) -> Dict[str, Any]:
        """Analyze biodiversity in Michigan using sample-based approach"""
        try:
            # Create sample points across Michigan
            sample_points = self._create_sample_points(20)
            
            # Get EVI from MODIS for sample points
            modis = ee.ImageCollection('MODIS/061/MOD13Q1') \
                .filterDate('2022-01-01', '2024-01-01') \
                .filterBounds(geometry) \
                .select('EVI')
            
            evi_sample = modis.mean().sampleRegions(
                collection=sample_points,
                scale=1000
            )
            
            evi_values = evi_sample.aggregate_array('EVI').getInfo()
            evi_mean = sum(evi_values) / len(evi_values) if evi_values else 0
            
            # Calculate biodiversity index from EVI
            biodiversity_index = min(1.0, max(0.0, evi_mean * 2))
            
            return {
                "biodiversity_index": round(biodiversity_index, 3),
                "species_count": int(biodiversity_index * 100)
            }
        except Exception as e:
            print(f"Biodiversity analysis error: {e}")
            raise e

    def _analyze_wildfire_michigan(self, geometry: ee.Geometry) -> Dict[str, Any]:
        """Analyze wildfire risk in Michigan using sample-based approach"""
        try:
            # Create sample points across Michigan
            sample_points = self._create_sample_points(20)
            
            # Get fire data for sample points
            fire_data = ee.ImageCollection('MODIS/061/MOD14A1') \
                .filterDate('2022-01-01', '2024-01-01') \
                .filterBounds(geometry) \
                .select('FireMask')
            
            fire_sample = fire_data.sum().sampleRegions(
                collection=sample_points,
                scale=1000
            )
            
            fire_values = fire_sample.aggregate_array('FireMask').getInfo()
            wildfire_count = sum(fire_values) if fire_values else 0
            
            # Determine risk level based on sample
            if wildfire_count > 20:
                risk_level = "High"
            elif wildfire_count > 10:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            return {
                "wildfire_count": int(wildfire_count),
                "risk_level": risk_level
            }
        except Exception as e:
            print(f"Wildfire analysis error: {e}")
            raise e

    def _analyze_wetlands_michigan(self, geometry: ee.Geometry) -> Dict[str, Any]:
        """Analyze wetlands in Michigan using sample-based approach"""
        try:
            # Create sample points across Michigan
            sample_points = self._create_sample_points(20)
            
            # Get MODIS data and calculate NDWI for sample points
            modis = ee.ImageCollection('MODIS/061/MOD13Q1') \
                .filterDate('2022-01-01', '2024-01-01') \
                .filterBounds(geometry)
            
            # Calculate NDWI from MODIS bands (NIR and SWIR)
            def add_ndwi(image):
                ndwi = image.normalizedDifference(['sur_refl_b02', 'sur_refl_b07']).rename('NDWI')
                return image.addBands(ndwi)
            
            modis_with_ndwi = modis.map(add_ndwi)
            ndwi_sample = modis_with_ndwi.select('NDWI').mean().sampleRegions(
                collection=sample_points,
                scale=1000
            )
            
            ndwi_values = ndwi_sample.aggregate_array('NDWI').getInfo()
            water_pixel_ratio = sum(1 for v in ndwi_values if v > 0.3) / len(ndwi_values) if ndwi_values else 0
            
            # Estimate wetland area from sample ratio
            michigan_area_km2 = 250493.0
            wetland_area_km2 = water_pixel_ratio * michigan_area_km2
            
            return {
                "wetland_area_km2": round(wetland_area_km2, 2),
                "water_quality_index": min(1.0, water_pixel_ratio)
            }
        except Exception as e:
            print(f"Wetlands analysis error: {e}")
            raise e

    def _analyze_water_quality_michigan(self, geometry: ee.Geometry) -> Dict[str, Any]:
        """Analyze water quality in Michigan using sample-based approach"""
        try:
            # Create sample points across Michigan
            sample_points = self._create_sample_points(20)
            
            # Get MODIS data and calculate NDWI for sample points
            modis = ee.ImageCollection('MODIS/061/MOD13Q1') \
                .filterDate('2022-01-01', '2024-01-01') \
                .filterBounds(geometry)
            
            # Calculate NDWI from MODIS bands (NIR and SWIR)
            def add_ndwi(image):
                ndwi = image.normalizedDifference(['sur_refl_b02', 'sur_refl_b07']).rename('NDWI')
                return image.addBands(ndwi)
            
            modis_with_ndwi = modis.map(add_ndwi)
            ndwi_sample = modis_with_ndwi.select('NDWI').mean().sampleRegions(
                collection=sample_points,
                scale=1000
            )
            
            ndwi_values = ndwi_sample.aggregate_array('NDWI').getInfo()
            ndwi_mean = sum(ndwi_values) / len(ndwi_values) if ndwi_values else 0
            
            # Calculate water quality index from NDWI
            water_quality_index = min(1.0, max(0.0, (ndwi_mean + 1) / 2))
            
            return {
                "water_quality_index": round(water_quality_index, 3),
                "turbidity_level": "Low" if water_quality_index > 0.7 else "Medium" if water_quality_index > 0.4 else "High"
            }
        except Exception as e:
            print(f"Water quality analysis error: {e}")
            raise e

    def _analyze_air_quality_michigan(self, geometry: ee.Geometry) -> Dict[str, Any]:
        """Analyze air quality in Michigan using sample-based approach"""
        try:
            # Create sample points across Michigan
            sample_points = self._create_sample_points(20)
            
            # Get aerosol data for sample points
            modis_aerosol = ee.ImageCollection('MODIS/006/MOD04_L2') \
                .filterDate('2022-01-01', '2024-01-01') \
                .filterBounds(geometry) \
                .select('Optical_Depth_Land_And_Ocean')
            
            aerosol_sample = modis_aerosol.mean().sampleRegions(
                collection=sample_points,
                scale=1000
            )
            
            aerosol_values = aerosol_sample.aggregate_array('Optical_Depth_Land_And_Ocean').getInfo()
            aerosol_mean = sum(aerosol_values) / len(aerosol_values) if aerosol_values else 0.2
            
            # Calculate air quality index from aerosol data
            air_quality_index = min(1.0, max(0.0, 1 - aerosol_mean))
            
            return {
                "air_quality_index": round(air_quality_index, 3),
                "aerosol_optical_depth": round(aerosol_mean, 3)
            }
        except Exception as e:
            print(f"Air quality analysis error: {e}")
            raise e


    # === LEAFLAP VISUALIZATION ===
    
    def create_michigan_visualization(self, query: str, visualization_type: str, stats: Dict[str, Any]) -> str:
        """Create simple coordinate-based map visualization for Michigan"""
        try:
            # Michigan center coordinates
            michigan_center = [44.3148, -85.6024]
            
            m = leafmap.Map(
                center=michigan_center,
                zoom=6,  # Show entire Michigan
                height=600
            )
            
            # Always use satellite view for environmental data
            m.add_basemap("SATELLITE")
            
            # Add Michigan bounding box
            import folium
            folium.Rectangle(
                bounds=[[41, -90], [48, -82]],  # [south, west], [north, east]
                color="red",
                weight=3,
                fill=False,
                popup="Michigan Analysis Region"
            ).add_to(m)
            
            # Add coordinate-based environmental markers
            self._add_environmental_coordinates(m, query, stats)
            
            # Add key Michigan reference points
            self._add_michigan_reference_points(m)
            
            # Add simple legend
            self._add_simple_legend(m, query, stats)
            
            # Generate filename and save
            filename = f"michigan_map_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(self.static_dir, filename)
            m.to_image(filename=filepath, width=1200, height=800)
            
            return f"/static/images/{filename}"
            
        except Exception as e:
            print(f"Visualization error: {e}")
            return "/static/images/michigan_placeholder.png"

    def _add_environmental_coordinates(self, m, query: str, stats: Dict[str, Any]):
        """Add coordinate-based environmental markers"""
        # Define Michigan environmental monitoring points with coordinates
        monitoring_points = [
            {"name": "Detroit Metro", "coords": [42.3314, -83.0458], "type": "urban"},
            {"name": "Saginaw Bay", "coords": [43.5, -83.5], "type": "wetland"},
            {"name": "Grand Rapids", "coords": [42.9634, -85.6681], "type": "urban"},
            {"name": "Upper Peninsula", "coords": [46.4, -87.4], "type": "forest"},
            {"name": "Mackinac Bridge", "coords": [45.8174, -84.7278], "type": "water"},
            {"name": "Traverse City", "coords": [44.7631, -85.6206], "type": "coastal"},
            {"name": "Lansing", "coords": [42.7325, -84.5555], "type": "urban"},
            {"name": "Marquette", "coords": [46.5436, -87.3953], "type": "forest"},
        ]
        
        # Add markers based on query type and environmental data
        for point in monitoring_points:
            # Determine marker color based on environmental indicators
            if "deforestation" in query.lower():
                color = "red" if stats.get("deforestation_rate", 0) > 5 else "green"
            elif "biodiversity" in query.lower():
                color = "green" if stats.get("biodiversity_index", 0) > 0.7 else "orange"
            elif "wildfire" in query.lower():
                color = "red" if stats.get("wildfire_count", 0) > 10 else "green"
            elif "water" in query.lower():
                color = "blue" if stats.get("water_quality_index", 0) > 0.6 else "red"
            else:
                color = "blue"
            
            # Add marker with coordinates
            m.add_circle_marker(
                location=point["coords"],
                radius=12,
                popup=f"{point['name']}<br>Type: {point['type']}<br>Coords: {point['coords'][0]:.4f}, {point['coords'][1]:.4f}",
                color=color,
                weight=3,
                fill=True,
                fillOpacity=0.7
            )

    def _add_choropleth_visualization(self, m, query: str, stats: Dict[str, Any]):
        """Add choropleth visualization for Michigan"""
        # Add colored regions based on environmental data
        michigan_regions = [
            {"name": "Upper Peninsula", "bounds": [[45.1, -90.4], [48.2, -83.6]], "value": stats.get("biodiversity_index", 0.5)},
            {"name": "Lower Peninsula", "bounds": [[41.7, -90.4], [45.1, -82.1]], "value": stats.get("deforestation_rate", 0) / 20},
        ]
        
        for region in michigan_regions:
            color = self._get_choropleth_color(region["value"])
            m.add_rectangle(
                bounds=region["bounds"],
                color=color,
                weight=2,
                fill=True,
                fillOpacity=0.6,
                popup=f"{region['name']}: {region['value']:.2f}"
            )

    def _get_choropleth_color(self, value: float) -> str:
        """Get color for choropleth based on value"""
        if value > 0.7:
            return "green"
        elif value > 0.4:
            return "yellow"
        else:
            return "red"

    def _add_michigan_locations(self, m, query: str):
        """Add key Michigan locations"""
        locations = [
            {"name": "Detroit", "coords": [42.3314, -83.0458], "color": "blue"},
            {"name": "Grand Rapids", "coords": [42.9634, -85.6681], "color": "green"},
            {"name": "Saginaw Bay", "coords": [43.5, -83.5], "color": "purple"},
            {"name": "Upper Peninsula", "coords": [46.4, -87.4], "color": "orange"},
        ]
        
        for location in locations:
            m.add_circle_marker(
                location=location["coords"],
                radius=8,
                popup=location["name"],
                color=location["color"],
                weight=2,
                fill=True,
                fillOpacity=0.8
            )

    def _add_michigan_legend(self, m, query: str, visualization_type: str, stats: Dict[str, Any]):
        """Add legend for Michigan visualization"""
        legend_html = f"""
        <div style="position: fixed; top: 10px; left: 10px; background: white; padding: 15px; border: 2px solid #333; border-radius: 8px; font-family: Arial, sans-serif; font-size: 12px; z-index: 1000; max-width: 300px;">
            <h3 style="margin: 0 0 10px 0; color: #333;">Michigan Environmental Analysis</h3>
            <p style="margin: 5px 0;"><strong>Query:</strong> {query}</p>
            <p style="margin: 5px 0;"><strong>Type:</strong> {visualization_type.title()}</p>
            <hr style="margin: 10px 0;">
            <p style="margin: 5px 0;"><strong>Area:</strong> {stats.get('area_affected', 'N/A'):,.0f} km²</p>
            <p style="margin: 5px 0;"><strong>Species:</strong> {stats.get('species_count', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Risk Level:</strong> {stats.get('risk_level', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Deforestation:</strong> {stats.get('deforestation_rate', 'N/A')}%</p>
            <p style="margin: 5px 0;"><strong>Biodiversity:</strong> {stats.get('biodiversity_index', 'N/A')}</p>
            <p style="margin: 5px 0;"><strong>Wildfires:</strong> {stats.get('wildfire_count', 'N/A')}</p>
        </div>
        """
        m.add_html(legend_html)

    # === GEMINI CONTENT GENERATION ===
    
    async def generate_summary_with_context(self, query: str, stats: Dict[str, Any], sources: List[str]) -> Dict[str, Any]:
        """Generate summary combining real GEE data with Gemini context"""
        self._ensure_initialized()
        
        if not self.model:
            return self._get_fallback_summary(query, stats, sources)

        try:
            # Convert any Earth Engine objects to Python native types for JSON serialization
            safe_stats = self._convert_ee_objects_to_python(stats)
            stats_str = json.dumps(safe_stats, indent=2)
            sources_str = json.dumps(sources, indent=2)
            prompt = f"""
You are a friendly environmental educator helping people understand Michigan's environment. Write a clear, easy-to-understand summary about environmental issues in Michigan.

Input:
- Query: "{query}"
- Real Data: {stats_str}
- Sources: {sources_str}
- Bounding Box: [-90, 41, -82, 48] (Michigan)

Instructions:
1. Write like you're talking to a friend about Michigan's environment
2. ONLY mention data that has real values (not null, None, or N/A)
3. If we don't have specific data, talk about what we know about Michigan's nature in general
4. Be honest but positive - don't mention missing data or technical problems
5. Use words like "amazing", "beautiful", "important" - make it engaging
6. Focus on why this matters to people and wildlife in Michigan
7. Keep it to 3-4 sentences that feel like a friendly conversation
8. Make people excited about learning about Michigan's environment

Output JSON structure:
{{
    "text": "A friendly, easy-to-understand summary about the environmental topic in Michigan.",
    "stats": {{
        "deforestation_area": "number in hectares (only if we have real data)",
        "biodiversity_index": "number or description (only if we have real data)",
        "wildfire_risk_index": "number or description (only if we have real data)",
        "wetlands_health": "number or description (only if we have real data)",
        "water_quality_index": "number or description (only if we have real data)",
        "air_quality_index": "number or description (only if we have real data)"
    }},
    "sources": [
        {{"name": "Michigan DNR", "url": "https://www.michigan.gov/dnr"}},
        {{"name": "...", "url": "..."}}
    ],
    "flags": {{
        "not_michigan": false,
        "not_relevant": false
    }}
}}

Focus on Michigan's environment, use relatively language that most people could understand, and help people learn about  specific things they could doprotecting our natural world.
"""
            
            response = self.model.generate_content(prompt)
            
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"Summary JSON decode error: {e}")
                print(f"Cleaned response: {response_text[:200]}...")
                return self._get_fallback_summary(query, stats, sources)
            
            # Ensure stats match our schema
            stats_obj = {
                "area_affected": stats.get("area_affected"),
                "species_count": stats.get("species_count"),
                "risk_level": stats.get("risk_level"),
                "deforestation_rate": stats.get("deforestation_rate"),
                "biodiversity_index": stats.get("biodiversity_index"),
                "wildfire_count": stats.get("wildfire_count")
            }
            
            # Process sources to ensure they are strings
            processed_sources = []
            if "sources" in result:
                for source in result["sources"]:
                    if isinstance(source, dict):
                        processed_sources.append(source.get("name", str(source)))
                    else:
                        processed_sources.append(str(source))
            else:
                processed_sources = sources
            
            # Process relevant metrics
            relevant_metrics = result.get("relevant_metrics", [])
            if not relevant_metrics and "key_metrics" in result:
                # If we have key_metrics but no detailed relevant_metrics, create them
                try:
                    all_metrics = GEEMetricsCatalog.get_all_metrics()
                    relevant_metrics = []
                    for metric_id in result["key_metrics"][:5]:  # Limit to 5
                        if metric_id in all_metrics:
                            metric_info = all_metrics[metric_id]
                            relevant_metrics.append({
                                "id": metric_id,
                                "name": metric_info["name"],
                                "description": metric_info["description"],
                                "category": metric_info["category"].value,
                                "relevance_score": 0.8,  # Default score
                                "range": metric_info.get("range"),
                                "datasets": metric_info.get("datasets")
                            })
                except Exception as e:
                    print(f"Error processing metrics: {e}")
                    relevant_metrics = []
            
            return {
                "text": result.get("text", f"Environmental analysis of {query} in Michigan using real satellite data."),
                "stats": stats_obj,
                "sources": processed_sources,
                "key_metrics": result.get("key_metrics", []),
                "relevant_metrics": relevant_metrics
            }
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return self._get_fallback_summary(query, stats, sources)

    def _get_fallback_summary(self, query: str, stats: Dict[str, Any], sources: List[str]) -> Dict[str, Any]:
        """Fallback summary when Gemini is not available"""
        return {
            "text": f"Unable to generate environmental analysis for {query} - AI services unavailable.",
            "stats": {
                "area_affected": stats.get("area_affected"),
                "species_count": None,
                "risk_level": None,
                "deforestation_rate": None,
                "biodiversity_index": None,
                "wildfire_count": None
            },
            "sources": [],
            "key_metrics": [],
            "relevant_metrics": []
        }

    async def generate_resources(self, query: str, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable resources using Gemini"""
        self._ensure_initialized()
        
        if not self.model:
            return self._get_fallback_resources(query)

        try:
            # Convert any Earth Engine objects to Python native types for JSON serialization
            safe_stats = self._convert_ee_objects_to_python(stats)
            
            prompt = f"""
            Find relevant Michigan environmental organizations and resources for this query:
            
            Query: "{query}"
            Environmental Data: {json.dumps(safe_stats, indent=2)}
            
            Generate:
            1. charities: Array of Michigan environmental organizations with name, url, description
            2. shareableUrl: Unique URL to recreate results
            
            Focus on Michigan-specific organizations and resources.
            """
            
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            return {
                "charities": result.get("charities", self._get_default_charities()),
                "shareableUrl": f"https://enviducate.com/share/{uuid.uuid4().hex[:8]}"
            }
            
        except Exception as e:
            print(f"Resources generation error: {e}")
            return self._get_fallback_resources(query)

    def _convert_ee_objects_to_python(self, obj: Any) -> Any:
        """Convert Earth Engine objects to Python native types for JSON serialization"""
        if hasattr(obj, 'getInfo'):
            # This is an Earth Engine object
            try:
                return obj.getInfo()
            except:
                return str(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_ee_objects_to_python(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_ee_objects_to_python(item) for item in obj]
        else:
            return obj

    def _get_fallback_resources(self, query: str) -> Dict[str, Any]:
        """Fallback resources when Gemini is not available"""
        return {
            "charities": [],
            "shareableUrl": ""
        }


    # === MAIN PROCESSING METHOD ===
    
    async def process_enviducate_query_simple(self, query: str) -> Dict[str, Any]:
        """Simplified query processing - only returns summary"""
        try:
            # Generate request ID and timestamp
            request_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Process query with Gemini to get indicators and context
            gemini_result = await self.process_query_with_gemini(query)
            indicators = gemini_result.get("indicators", ["deforestation", "biodiversity", "wildfire"])
            
            # Analyze with Google Earth Engine
            stats_data = await self.analyze_michigan_environment(query, indicators)
            
            # Generate summary
            summary = await self.generate_summary_with_context(
                query, 
                stats_data, 
                gemini_result.get("sources", ["Michigan DNR", "Google Earth Engine"])
            )
            
            return {
                "summary": summary,
                "request_id": request_id,
                "timestamp": timestamp
            }
            
        except Exception as e:
            print(f"Simple query processing error: {e}")
            raise e

    async def process_enviducate_query(self, query: str, visualization_type: str) -> Dict[str, Any]:
        """Main method to process Enviducate query with caching"""
        # Check cache first
        cache_key = self._get_cache_key(query, visualization_type)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            print(f"Using cached result for query: {query}")
            return cached_result
        
        # Process query with Gemini and Google Search
        gemini_result = await self.process_query_with_gemini(query)
        indicators = gemini_result.get("indicators", ["deforestation", "biodiversity", "wildfire"])
        
        # Process sources to ensure they are strings
        raw_sources = gemini_result.get("sources", ["Michigan DNR", "Google Earth Engine"])
        sources = []
        for source in raw_sources:
            if isinstance(source, dict):
                sources.append(source.get("name", str(source)))
            else:
                sources.append(str(source))
        
        # Analyze with Google Earth Engine (Michigan bounding box)
        stats = await self.analyze_michigan_environment(query, indicators)
        
        # Create Michigan-focused visualization
        visualization_url = self.create_michigan_visualization(query, visualization_type, stats)
        
        # Generate summary with real data + Gemini context
        summary_data = await self.generate_summary_with_context(query, stats, sources)
        
        # Generate resources
        resources_data = await self.generate_resources(query, stats)
        
        # Assemble response
        result = {
            "summary": summary_data,
            "visualization": {
                "url": visualization_url,
                "type": visualization_type,
                "legend": {
                    "blue": "Low Impact",
                    "yellow": "Medium Impact", 
                    "red": "High Impact"
                }
            },
            "resources": resources_data,
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Cache result
        self._cache_result(cache_key, result)
        
        return result
