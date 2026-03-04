from typing import List
import io
import numpy as np
import cv2
from PIL import Image
from app.models.schemas import ExtractedSignal

async def analyze(image_bytes: bytes) -> List[ExtractedSignal]:
    """
    Multi-signal forensic analysis combining:
    1. Fourier Spectrum Analysis - detect periodic AI artifacts
    2. Error Level Analysis (ELA) - detect synthetic compression uniformity
    3. Noise Residual Analysis - detect unnatural noise patterns
    """
    signals = []
    
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
             raise ValueError("OpenCV could not decode image bytes.")

        # ---- 1. Fourier Spectrum Analysis ----
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
        spectrum_variance = float(np.var(magnitude_spectrum))
        
        # ---- 2. Error Level Analysis (ELA) ----
        _, encoded_img = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        resaved_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
        ela_diff = cv2.absdiff(img, resaved_img)
        ela_mean = float(np.mean(ela_diff))
        ela_std = float(np.std(ela_diff))
        
        # ---- 3. Median Filter Noise Residual ----
        median = cv2.medianBlur(img, 3)
        noise = cv2.absdiff(img, median)
        noise_std = float(np.std(noise))
        
        # ---- Scoring ----
        # ELA: AI images have very uniform error levels (low std, low mean)
        ela_score = 0.0
        if ela_std < 2.0 and ela_mean < 1.2:
            ela_score = 0.7
        elif ela_std < 3.5 and ela_mean < 2.5:
            ela_score = 0.4
        elif ela_std < 5.0:
            ela_score = 0.15
            
        # Noise: Real photos have higher noise residual std (3-12)
        # AI images are smoother (0.5-3)
        noise_score = 0.0
        if noise_std < 2.0:
            noise_score = 0.6
        elif noise_std < 4.0:
            noise_score = 0.3
        else:
            noise_score = 0.05
            
        # Fourier: unusually high / low spectrum variance 
        fourier_score = 0.0
        if spectrum_variance > 500:
            fourier_score = 0.5
        elif spectrum_variance < 100:
            fourier_score = 0.3
        
        combined = round(min(
            ela_score * 0.40 + noise_score * 0.35 + fourier_score * 0.25,
            0.99
        ), 4)
        
        signal_name = "synthetic_forensic_traces" if combined > 0.3 else "natural_forensic_profile"
        
        signals.append(ExtractedSignal(
            detector="forensic_analysis",
            signal_name=signal_name,
            confidence=combined,
            details={
                "spectrum_variance": round(spectrum_variance, 2), 
                "ela_std": round(ela_std, 3),
                "ela_mean": round(ela_mean, 3),
                "noise_residual_std": round(noise_std, 3),
                "ela_score": round(ela_score, 3),
                "noise_score": round(noise_score, 3), 
                "fourier_score": round(fourier_score, 3),
                "technique": "ELA + Noise Residual + Fourier"
            }
        ))
        
    except Exception as e:
        signals.append(ExtractedSignal(
            detector="forensic_analysis",
            signal_name="processing_error",
            confidence=0.01,
            details={"error": str(e)}
        ))
        
    return signals
