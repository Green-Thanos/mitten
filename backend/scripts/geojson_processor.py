#!/usr/bin/env python3
"""
GeoJSON Processing Pipeline
Processes GeoJSON files, extracts coordinates, and generates summaries using Gemini AI
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from app.core.config import settings


class GeoJSONProcessor:
    """Processes GeoJSON files and generates environmental summaries"""
    
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def extract_coordinates(self, geojson: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract coordinates from GeoJSON features"""
        coords = []
        
        if 'features' not in geojson:
            print("❌ Invalid GeoJSON: No features found")
            return coords
        
        for feature in geojson['features']:
            label = feature.get('properties', {}).get('FieldName', 'Unknown')
            geometry = feature.get('geometry', {})
            
            if geometry.get('type') == 'Polygon':
                for ring in geometry['coordinates']:
                    for coord in ring:
                        if len(coord) >= 2:
                            coords.append({
                                'lat': coord[1],
                                'lng': coord[0],
                                'label': label
                            })
            
            elif geometry.get('type') == 'MultiPolygon':
                for polygon in geometry['coordinates']:
                    for ring in polygon:
                        for coord in ring:
                            if len(coord) >= 2:
                                coords.append({
                                    'lat': coord[1],
                                    'lng': coord[0],
                                    'label': label
                                })
            
            elif geometry.get('type') == 'Point':
                coord = geometry['coordinates']
                if len(coord) >= 2:
                    coords.append({
                        'lat': coord[1],
                        'lng': coord[0],
                        'label': label
                    })
        
        return coords
    
    def sample_coordinates(self, coords: List[Dict[str, Any]], n: int = 50) -> List[Dict[str, Any]]:
        """Sample coordinates evenly"""
        if len(coords) <= n:
            return coords
        
        step = max(len(coords) // n, 1)
        sampled = []
        for i in range(0, len(coords), step):
            if len(sampled) < n:
                sampled.append(coords[i])
        
        return sampled
    
    def analyze_geojson_with_gemini(self, file_path: str, coords: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use Gemini AI to analyze the GeoJSON data and generate summary"""
        if not self.model:
            return self._generate_fallback_analysis(file_path, coords)
        
        try:
            # Prepare context for Gemini
            context = f"""
            Analyze this GeoJSON data from file: {file_path}
            
            Data summary:
            - Total coordinates: {len(coords)}
            - Sample coordinates: {coords[:5]}...
            
            Please provide:
            1. A descriptive title for this environmental data
            2. A category (energy, water, forest, wildlife, etc.)
            3. A comprehensive summary explaining what this data represents
            4. Key environmental insights
            5. Potential environmental concerns or opportunities
            6. Suggested sources for this data
            
            Format as JSON with these fields:
            {{
                "title": "string",
                "category": "string", 
                "summary": "string",
                "insights": ["string"],
                "concerns": ["string"],
                "sources": ["string"]
            }}
            """
            
            response = self.model.generate_content(context)
            result = json.loads(response.text)
            
            return result
            
        except Exception as e:
            print(f"❌ Gemini analysis failed: {e}")
            return self._generate_fallback_analysis(file_path, coords)
    
    def _generate_fallback_analysis(self, file_path: str, coords: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback analysis when Gemini is not available"""
        filename = Path(file_path).stem
        
        return {
            "title": f"Environmental Data: {filename}",
            "category": "environmental",
            "summary": f"Geospatial data containing {len(coords)} coordinate points from {filename}. This data represents environmental features or monitoring points in Michigan.",
            "insights": [
                f"Contains {len(coords)} data points",
                "Located in Michigan region",
                "Geospatial environmental data"
            ],
            "concerns": [
                "Data quality needs verification",
                "Coordinate accuracy should be validated"
            ],
            "sources": [
                "Michigan Environmental Data",
                "Geospatial Analysis"
            ]
        }
    
    def process_geojson_file(self, input_path: str, output_dir: str) -> Dict[str, Any]:
        """Process a single GeoJSON file"""
        print(f"🔄 Processing: {input_path}")
        
        try:
            # Load GeoJSON
            with open(input_path, 'r', encoding='utf-8') as f:
                geojson = json.load(f)
            
            # Extract coordinates
            all_coords = self.extract_coordinates(geojson)
            if not all_coords:
                print(f"❌ No coordinates found in {input_path}")
                return None
            
            # Sample coordinates
            sampled_coords = self.sample_coordinates(all_coords, 50)
            
            # Analyze with Gemini
            analysis = self.analyze_geojson_with_gemini(input_path, sampled_coords)
            
            # Generate output data
            output_data = {
                "id": str(uuid.uuid4()),
                "originalQuery": analysis.get("title", "Environmental Data"),
                "category": analysis.get("category", "environmental"),
                "summary": analysis.get("summary", "Environmental data analysis"),
                "sources": analysis.get("sources", ["Michigan Environmental Data"]),
                "charities": self._get_relevant_charities(analysis.get("category", "environmental")),
                "visualizations": [
                    {
                        "type": "pinpoints",
                        "data": sampled_coords,
                        "metadata": {
                            "title": analysis.get("title", "Environmental Data"),
                            "description": analysis.get("summary", "Environmental data visualization"),
                            "source": "Michigan Environmental Data",
                            "lastUpdated": datetime.now().isoformat(),
                            "totalPoints": len(all_coords),
                            "sampledPoints": len(sampled_coords)
                        }
                    }
                ],
                "shareableUrl": f"https://enviducate.org/result/{str(uuid.uuid4())[:8]}",
                "generatedAt": datetime.now().isoformat(),
                "insights": analysis.get("insights", []),
                "concerns": analysis.get("concerns", [])
            }
            
            # Save output
            output_filename = f"{Path(input_path).stem}_processed.json"
            output_path = os.path.join(output_dir, output_filename)
            
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Processed: {output_path}")
            return output_data
            
        except Exception as e:
            print(f"❌ Error processing {input_path}: {e}")
            return None
    
    def _get_relevant_charities(self, category: str) -> List[Dict[str, str]]:
        """Get relevant charities based on category"""
        charity_map = {
            "energy": [
                {"name": "Michigan Environmental Council", "url": "https://www.environmentalcouncil.org", "description": "Advocating for clean energy in Michigan"},
                {"name": "Sierra Club Michigan", "url": "https://www.sierraclub.org/michigan", "description": "Environmental protection and clean energy advocacy"}
            ],
            "water": [
                {"name": "Great Lakes Protection Fund", "url": "https://www.glpf.org", "description": "Protecting the Great Lakes ecosystem"},
                {"name": "Michigan Environmental Council", "url": "https://www.environmentalcouncil.org", "description": "Water quality protection in Michigan"}
            ],
            "forest": [
                {"name": "Michigan Nature Association", "url": "https://www.michigannature.org", "description": "Protecting Michigan's natural areas and forests"},
                {"name": "The Nature Conservancy Michigan", "url": "https://www.nature.org/michigan", "description": "Forest conservation and restoration"}
            ],
            "wildlife": [
                {"name": "Michigan Audubon", "url": "https://www.michiganaudubon.org", "description": "Bird and wildlife conservation"},
                {"name": "Michigan Nature Association", "url": "https://www.michigannature.org", "description": "Wildlife habitat protection"}
            ]
        }
        
        return charity_map.get(category, [
            {"name": "Michigan Environmental Council", "url": "https://www.environmentalcouncil.org", "description": "Environmental protection in Michigan"},
            {"name": "The Nature Conservancy Michigan", "url": "https://www.nature.org/michigan", "description": "Conservation and environmental protection"}
        ])
    
    def process_directory(self, input_dir: str, output_dir: str) -> List[Dict[str, Any]]:
        """Process all GeoJSON files in a directory"""
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"❌ Input directory not found: {input_dir}")
            return []
        
        geojson_files = list(input_path.glob("*.geojson")) + list(input_path.glob("*.json"))
        if not geojson_files:
            print(f"❌ No GeoJSON files found in {input_dir}")
            return []
        
        print(f"🔄 Found {len(geojson_files)} GeoJSON files to process")
        
        results = []
        for file_path in geojson_files:
            result = self.process_geojson_file(str(file_path), output_dir)
            if result:
                results.append(result)
        
        print(f"✅ Processed {len(results)} files successfully")
        return results


def main():
    """Main function for command line usage"""
    if len(sys.argv) < 3:
        print("Usage: python geojson_processor.py <input_path> <output_dir>")
        print("  input_path: Path to GeoJSON file or directory")
        print("  output_dir: Directory to save processed files")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    processor = GeoJSONProcessor()
    
    if os.path.isfile(input_path):
        # Process single file
        result = processor.process_geojson_file(input_path, output_dir)
        if result:
            print("✅ Single file processing completed")
        else:
            print("❌ Single file processing failed")
    else:
        # Process directory
        results = processor.process_directory(input_path, output_dir)
        if results:
            print(f"✅ Directory processing completed: {len(results)} files processed")
        else:
            print("❌ Directory processing failed")


if __name__ == "__main__":
    main()

