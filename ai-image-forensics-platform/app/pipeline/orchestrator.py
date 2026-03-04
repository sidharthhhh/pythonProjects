import asyncio
from app.models.schemas import DetectorResult, ExtractedSignal

from app.detectors import (
    metadata,
    c2pa_verifier,
    watermark,
    ai_classifier,
    forensic,
    manipulation,
    diffusion,
)

async def run_analysis_pipeline(image_bytes: bytes) -> dict:
    """
    Orchestrates the asynchronous execution of all detection modules.
    We run checks concurrently to maximize throughput.
    """
    # Create asynchronous tasks for each standalone detector
    # (assuming all detectors implement an async `analyze` function taking raw bytes)
    
    tasks = [
        metadata.analyze(image_bytes),
        c2pa_verifier.analyze(image_bytes),
        watermark.analyze(image_bytes),
        ai_classifier.analyze(image_bytes),
        forensic.analyze(image_bytes),
        manipulation.analyze(image_bytes),
        diffusion.analyze(image_bytes)
    ]
    
    # Wait for all detectors to complete their analysis
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Collate results handling any potential failures smoothly (security_first, handle_all_edge_cases)
    signals = []
    
    detector_names = [
        "metadata", "c2pa", "watermark", "ai_classifier", "forensic", "manipulation", "diffusion"
    ]
    
    detector_outputs = {}
    
    for idx, res in enumerate(results):
        name = detector_names[idx]
        if isinstance(res, Exception):
            # Log failure but do not crash the pipeline
            detector_outputs[name] = {"error": str(res)}
        else:
            detector_outputs[name] = res
            if res and isinstance(res, list): # List of ExtractedSignal
                 signals.extend(res)
            elif res and isinstance(res, ExtractedSignal):
                 signals.append(res)
                 
    return {
        "raw_outputs": detector_outputs,
        "combined_signals": signals
    }
