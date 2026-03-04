import torch
import torchvision.transforms as T
import io
import numpy as np
from PIL import Image
from typing import List
from app.models.schemas import ExtractedSignal

async def analyze(image_bytes: bytes) -> List[ExtractedSignal]:
    """
    Multi-layered AI classifier combining:
    1. Resolution pattern matching (common AI output sizes)
    2. Color histogram analysis (AI images have distinctive distributions)
    3. Edge density analysis (AI images often have fewer sharp micro-edges)
    4. Pixel value entropy (AI images have different entropy profiles)
    """
    signals = []
    
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = image.size
        img_array = np.array(image)
        
        # ---- Signal 1: Resolution Pattern ----
        common_ai_dims = [
            (512, 512), (768, 768), (1024, 1024),
            (1024, 1792), (1792, 1024),
            (896, 1152), (1152, 896),
            (1024, 768), (768, 1024),
            (256, 256), (640, 640),
        ]
        resolution_score = 0.0
        if (width, height) in common_ai_dims:
            resolution_score = 0.6
        elif width == height:  # Square images are much more common in AI
            resolution_score = 0.3
        
        # ---- Signal 2: Color Channel Statistics ----
        # AI images tend to have more uniform color distributions
        channel_stds = [np.std(img_array[:, :, c]) for c in range(3)]
        avg_channel_std = np.mean(channel_stds)
        channel_std_range = max(channel_stds) - min(channel_stds)
        
        # Very uniform channel distribution suggests AI
        color_score = 0.0
        if channel_std_range < 5.0:  # Channels are suspiciously similar
            color_score = 0.4
        if avg_channel_std < 40.0:  # Very narrow color range
            color_score += 0.2

        # ---- Signal 3: Local Edge Density ----
        # Use Sobel-like gradient via numpy to detect micro-edge density
        gray = np.mean(img_array, axis=2)
        dx = np.diff(gray, axis=1)
        dy = np.diff(gray, axis=0)
        edge_magnitude = np.sqrt(dx[:, :-1]**2 + dy[:-1, :]**2)
        
        # Count "strong micro-edges" (> 30 gradient)
        strong_edges_pct = np.sum(edge_magnitude > 30) / edge_magnitude.size
        
        # Real photos have lots of micro-texture edges (5-15%)
        # AI images are smoother (1-5%)
        edge_score = 0.0
        if strong_edges_pct < 0.03:
            edge_score = 0.5
        elif strong_edges_pct < 0.06:
            edge_score = 0.2
        
        # ---- Signal 4: Shannon Entropy ----
        # AI-generated images often have subtly different entropy
        hist, _ = np.histogram(gray.flatten(), bins=256, range=(0, 256), density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        
        # Natural photos typically have entropy 6.5-7.8
        # AI images can be lower (very clean) or artificially high
        entropy_score = 0.0
        if entropy < 6.0:
            entropy_score = 0.4
        elif entropy > 7.6:
            entropy_score = 0.15

        # ---- Combine All Signals ----
        combined_score = (
            resolution_score * 0.25 +
            color_score * 0.20 +
            edge_score * 0.35 +
            entropy_score * 0.20
        )
        combined_score = round(min(max(combined_score, 0.01), 0.99), 4)
        
        signal_name = "ai_texture_anomaly" if combined_score > 0.3 else "natural_texture"
        
        signals.append(ExtractedSignal(
            detector="ai_classifier",
            signal_name=signal_name,
            confidence=combined_score,
            details={
                "model": "statistical_heuristic_v2",
                "resolution_score": round(resolution_score, 3),
                "color_uniformity_score": round(color_score, 3),
                "edge_density_score": round(edge_score, 3),
                "edge_density_pct": round(float(strong_edges_pct), 4),
                "entropy_score": round(entropy_score, 3),
                "entropy": round(float(entropy), 3),
                "dimensions": f"{width}x{height}"
            }
        ))
             
    except Exception as e:
        signals.append(ExtractedSignal(
             detector="ai_classifier",
             signal_name="inference_error",
             confidence=0.01,
             details={"error": str(e)}
        ))

    return signals
