from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, BackgroundTasks
from app.models.schemas import AnalysisResponse
from app.core.security import validate_image_file, validate_file_size, verify_authentication
from app.pipeline.orchestrator import run_analysis_pipeline
from app.engine.decision import generate_decision
import uuid

router = APIRouter()

@router.post("/analyze", 
             response_model=AnalysisResponse, 
             dependencies=[Depends(verify_authentication), Depends(validate_file_size)],
             description="Analyze an image via multi-layer forensic detection to determine if it is AI-generated.")
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="The image file to upload (JPEG, PNG, WEBP, etc, max 50MB)"),
):
    # 1. Read and validate the file locally (size limit enforced by Depends middleware, magic number by validate_image_file)
    try:
        image_bytes = await validate_image_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    analysis_id = str(uuid.uuid4())
    
    # 2. Execute parallel processing pipeline
    pipeline_results = await run_analysis_pipeline(image_bytes)
    
    # 3. Aggregate results in the Decision Engine
    response = generate_decision(pipeline_results)
    
    return response
