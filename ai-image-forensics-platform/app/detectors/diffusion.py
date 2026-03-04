from typing import List
import numpy as np
import cv2
from app.models.schemas import ExtractedSignal

async def analyze(image_bytes: bytes) -> List[ExtractedSignal]:
    """
    Extracts the noise residual fingerprint to detect Diffusion model artifacts.
    Uses Non-Local Means Denoising + FFT analysis of the residual plane.
    Real images have high-variance natural sensor noise.
    AI images have low-variance synthetic noise with periodic FFT footprints.
    """
    signals = []
    
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
             raise ValueError("OpenCV could not decode image bytes.")
             
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Non-local Means Denoising to extract noise residual
        clean_img = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        noise_residual = cv2.absdiff(gray, clean_img)
        
        variance = float(np.var(noise_residual))
        mean_noise = float(np.mean(noise_residual))
        
        # 2. FFT of the noise residual to find periodic patterns
        f = np.fft.fft2(noise_residual)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)
        
        # Check if FFT has unusual periodic peaks (AI fingerprints)
        fft_std = float(np.std(magnitude_spectrum))
        fft_max = float(np.max(magnitude_spectrum))
        
        # 3. Score calculation
        # Real camera sensors: variance typically 15-60, mean_noise 2-8
        # AI diffusion: variance typically 2-12, mean_noise 0.5-3
        
        # Inverse mapping: lower variance = higher AI probability
        if variance < 5.0:
            noise_score = 0.9
        elif variance < 10.0:
            noise_score = 0.65
        elif variance < 18.0:
            noise_score = 0.35
        else:
            noise_score = 0.05
            
        # FFT periodicity check
        fft_score = 0.0
        if fft_std < 15.0:  # AI tends to have more uniform FFT
            fft_score = 0.3
            
        combined = round(min(noise_score * 0.7 + fft_score * 0.3, 0.99), 4)
        
        signal_name = "diffusion_synthetic_noise" if combined > 0.4 else "natural_sensor_noise"
        
        signals.append(ExtractedSignal(
            detector="diffusion_noise_fingerprint",
            signal_name=signal_name,
            confidence=combined,
            details={
                "noise_variance": round(variance, 4), 
                "mean_residual": round(mean_noise, 4),
                "fft_std": round(fft_std, 4),
                "noise_score": round(noise_score, 4),
                "fingerprint_type": "low_variance_synthetic" if combined > 0.4 else "high_variance_natural"
            }
        ))
            
    except Exception as e:
        signals.append(ExtractedSignal(
            detector="diffusion_noise_fingerprint",
            signal_name="processing_error",
            confidence=0.01,
            details={"error": str(e)}
        ))
        
    return signals
