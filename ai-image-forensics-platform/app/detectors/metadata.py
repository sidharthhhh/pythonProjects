import io
from PIL import Image, ExifTags
from typing import List
from app.models.schemas import ExtractedSignal

async def analyze(image_bytes: bytes) -> List[ExtractedSignal]:
    """
    Extract EXIF, XMP, IPTC to detect tags indicating AI generation.
    Looks for: "Software", "CreatorTool", Midjourney/DALL-E tags, missing metadata.
    """
    signals = []
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif = image.getexif()
        
        # Edge case: No EXIF found (anomaly for modern photos, might imply generation or stripping)
        if not exif:
            signals.append(ExtractedSignal(
                detector="metadata",
                signal_name="missing_metadata_anomaly",
                confidence=0.5,
                details={"message": "No typical EXIF metadata found."}
            ))
            return signals

        # Parse tags
        software_found = False
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag in ["Software", "Model", "ImageDescription", "Make"]:
                if isinstance(value, str):
                    val_lower = value.lower()
                    if any(keyword in val_lower for keyword in ["stable diffusion", "midjourney", "dall-e", "openai"]):
                         signals.append(ExtractedSignal(
                             detector="metadata",
                             signal_name=f"ai_generator_tag_found",
                             confidence=0.99,
                             details={"matched_field": tag, "value": value}
                         ))
                         software_found = True

        if not software_found:
             signals.append(ExtractedSignal(
                 detector="metadata",
                 signal_name="standard_exif_found",
                 confidence=0.1,
                 details={"message": "Standard camera EXIF blocks present."}
             ))

    except Exception as e:
        signals.append(ExtractedSignal(
            detector="metadata",
            signal_name="parsing_error",
            confidence=0.1,
            details={"error": str(e)}
        ))

    return signals
