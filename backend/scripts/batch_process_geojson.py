#!/usr/bin/env python3
"""
Batch GeoJSON Processing Script
Processes multiple GeoJSON files with Gemini AI analysis
"""

import os
import sys
import json
import argparse
from pathlib import Path
from geojson_processor import GeoJSONProcessor


def setup_directories(input_dir: str, output_dir: str):
    """Setup input and output directories"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"✅ Output directory ready: {output_dir}")
    
    return input_path, output_path


def find_geojson_files(input_dir: Path) -> list:
    """Find all GeoJSON files in the input directory"""
    geojson_extensions = ['.geojson', '.json']
    files = []
    
    for ext in geojson_extensions:
        files.extend(input_dir.glob(f"*{ext}"))
    
    return sorted(files)


def create_processing_report(results: list, output_dir: Path):
    """Create a processing report"""
    report = {
        "processing_summary": {
            "total_files": len(results),
            "successful_files": len([r for r in results if r is not None]),
            "failed_files": len([r for r in results if r is None]),
            "timestamp": str(Path().cwd())
        },
        "processed_files": [
            {
                "filename": result.get("originalQuery", "Unknown"),
                "category": result.get("category", "Unknown"),
                "points_count": len(result.get("visualizations", [{}])[0].get("data", [])),
                "id": result.get("id", "Unknown")
            }
            for result in results if result is not None
        ]
    }
    
    report_path = output_dir / "processing_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Processing report saved: {report_path}")


def main():
    """Main batch processing function"""
    parser = argparse.ArgumentParser(description="Batch process GeoJSON files with Gemini AI")
    parser.add_argument("input_dir", help="Directory containing GeoJSON files")
    parser.add_argument("output_dir", help="Directory to save processed files")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum number of files to process")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without actually processing")
    
    args = parser.parse_args()
    
    print("🚀 Starting batch GeoJSON processing...")
    print(f"📁 Input directory: {args.input_dir}")
    print(f"📁 Output directory: {args.output_dir}")
    
    # Setup directories
    input_path, output_path = setup_directories(args.input_dir, args.output_dir)
    
    # Find GeoJSON files
    geojson_files = find_geojson_files(input_path)
    
    if not geojson_files:
        print("❌ No GeoJSON files found in input directory")
        sys.exit(1)
    
    print(f"📄 Found {len(geojson_files)} GeoJSON files")
    
    # Limit files if specified
    if args.max_files:
        geojson_files = geojson_files[:args.max_files]
        print(f"📄 Processing first {len(geojson_files)} files")
    
    if args.dry_run:
        print("🔍 Dry run - files that would be processed:")
        for file_path in geojson_files:
            print(f"  - {file_path.name}")
        return
    
    # Initialize processor
    processor = GeoJSONProcessor()
    
    # Process files
    results = []
    for i, file_path in enumerate(geojson_files, 1):
        print(f"\n🔄 Processing {i}/{len(geojson_files)}: {file_path.name}")
        
        try:
            result = processor.process_geojson_file(str(file_path), str(output_path))
            results.append(result)
            
            if result:
                print(f"✅ Success: {file_path.name}")
            else:
                print(f"❌ Failed: {file_path.name}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            results.append(None)
    
    # Create processing report
    create_processing_report(results, output_path)
    
    # Summary
    successful = len([r for r in results if r is not None])
    failed = len([r for r in results if r is None])
    
    print(f"\n📊 Batch processing complete!")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output directory: {output_path}")


if __name__ == "__main__":
    main()

