from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
from datetime import datetime
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisError, EnvironmentalStats
from app.services.gemini_service import GeminiService
from app.services.gee_service import GoogleEarthEngineService
from app.services.leafmap_service import LeafmapService

router = APIRouter()

# Services will be initialized lazily when needed


@router.post("/", response_model=AnalysisResponse)
async def analyze_environment(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze environmental data using Gemini, Google Earth Engine, and Leafmap.
    
    This endpoint processes natural language queries about environmental data,
    generates visualizations, and returns analysis results with statistics.
    """
    try:
        # Validate time range
        start_date = datetime.strptime(request.time_range.start, "%Y-%m-%d")
        end_date = datetime.strptime(request.time_range.end, "%Y-%m-%d")
        
        if start_date >= end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )
        
        # Step 1: Process query with Gemini
        gemini_service = GeminiService()
        gemini_result = await gemini_service.process_environmental_query(
            query=request.query,
            region=request.region,
            time_range={
                "start": request.time_range.start,
                "end": request.time_range.end
            }
        )
        
        indicators = gemini_result.get("indicators", ["deforestation", "biodiversity", "wildfire"])
        
        # Step 2: Analyze with Google Earth Engine
        gee_service = GoogleEarthEngineService()
        gee_results = await gee_service.process_environmental_analysis(
            region=request.region,
            start_date=request.time_range.start,
            end_date=request.time_range.end,
            indicators=indicators
        )
        
        # Step 3: Generate Leafmap visualization
        leafmap_service = LeafmapService()
        image_url = leafmap_service.create_environmental_map(
            region=request.region,
            start_date=request.time_range.start,
            end_date=request.time_range.end,
            indicators=indicators,
            stats=gee_results
        )
        
        # Step 4: Generate final summary with Gemini
        final_summary = await gemini_service.generate_analysis_summary(
            stats=gee_results,
            indicators=indicators
        )
        
        # Step 5: Prepare response
        stats = EnvironmentalStats(
            deforestation_rate=gee_results.get("deforestation_rate"),
            biodiversity_index=gee_results.get("biodiversity_index"),
            wildfire_count=gee_results.get("wildfire_count")
        )
        
        return AnalysisResponse(
            summary=final_summary,
            stats=stats,
            image_url=image_url
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/async", response_model=Dict[str, str])
async def analyze_environment_async(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Start environmental analysis asynchronously.
    
    This endpoint initiates analysis in the background and returns a task ID
    for checking status later.
    """
    task_id = str(uuid.uuid4())
    
    # Add background task
    background_tasks.add_task(
        _process_analysis_background,
        task_id,
        request
    )
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Analysis started in background"
    }


async def _process_analysis_background(task_id: str, request: AnalysisRequest):
    """
    Background task for processing environmental analysis.
    This can be extended to save results to a database or cache.
    """
    try:
        # Process the analysis (same logic as sync endpoint)
        start_date = datetime.strptime(request.time_range.start, "%Y-%m-%d")
        end_date = datetime.strptime(request.time_range.end, "%Y-%m-%d")
        
        gemini_service = GeminiService()
        gemini_result = await gemini_service.process_environmental_query(
            query=request.query,
            region=request.region,
            time_range={
                "start": request.time_range.start,
                "end": request.time_range.end
            }
        )
        
        indicators = gemini_result.get("indicators", ["deforestation", "biodiversity", "wildfire"])
        
        gee_service = GoogleEarthEngineService()
        gee_results = await gee_service.process_environmental_analysis(
            region=request.region,
            start_date=request.time_range.start,
            end_date=request.time_range.end,
            indicators=indicators
        )
        
        leafmap_service = LeafmapService()
        image_url = leafmap_service.create_environmental_map(
            region=request.region,
            start_date=request.time_range.start,
            end_date=request.time_range.end,
            indicators=indicators,
            stats=gee_results
        )
        
        final_summary = await gemini_service.generate_analysis_summary(
            stats=gee_results,
            indicators=indicators
        )
        
        # TODO: Save results to database or cache using task_id
        print(f"Background analysis completed for task {task_id}")
        
    except Exception as e:
        print(f"Background analysis failed for task {task_id}: {e}")
        # TODO: Save error status to database or cache
