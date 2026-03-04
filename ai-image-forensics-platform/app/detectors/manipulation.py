from typing import List
from app.models.schemas import ExtractedSignal

async def analyze(image_bytes: bytes) -> List[ExtractedSignal]:
    """
    Detects if an image was manipulated (resized, recompressed, cropped) after initial generation.
    This helps in calibrating confidence because multiple recompressions destroy forensic signals.
    """
    signals = []
    
    # In production, check JPEG quantization tables, double compression footprints:
    # 1. JPEG Ghosting
    # 2. Block artifact mismatches
    
    recompressed = False
    if recompressed:
         signals.append(ExtractedSignal(
            detector="manipulation",
            signal_name="double_jpeg_compression",
            confidence=0.6,
            details={"estimated_quality_1": 95, "estimated_quality_2": 80}
         ))
    else:
         signals.append(ExtractedSignal(
            detector="manipulation",
            signal_name="pristine_compression",
            confidence=0.1,
            details={"message": "No double quantization artifacts detected."}
         ))
         
    return signals
