from app.models.schemas import AnalysisResponse, ExtractedSignal
from typing import List, Dict

# Defines which signal names are POSITIVE AI indicators.
# Only these signals contribute to the AI probability score.
AI_SIGNAL_NAMES = {
    "ai_generator_tag_found",
    "missing_metadata_anomaly",
    "synthid_pattern_detected",
    # ai_classifier signals
    "ai_texture_anomaly",
    # forensic signals
    "synthetic_forensic_traces",
    # diffusion signals
    "diffusion_synthetic_noise",
    # manipulation signals
    "double_jpeg_compression",
}

# These detectors each get a "baseline" weight added to the denominator
# even when they return nothing, to prevent division-by-zero and to dilute
# the AI score when all detectors are clean.
DETECTOR_WEIGHTS = {
    "metadata": 0.4,
    "c2pa_verifier": 0.8,
    "watermark": 1.0,
    "ai_classifier": 0.9,
    "forensic_analysis": 0.7,
    "diffusion_noise_fingerprint": 0.85,
    "manipulation": 0.3,
}

def generate_decision(pipeline_results: dict) -> AnalysisResponse:
    """
    Calculates final AI probability using a strict whitelist approach.
    Only recognized AI-indicator signals contribute to the score numerator.
    Clean signals serve only to expand the denominator (diluting the score toward 0).
    """
    signals: List[ExtractedSignal] = pipeline_results["combined_signals"]

    ai_score_accum = 0.0
    
    c2pa_verified = False
    watermark_detected = False
    metadata_hint = False
    forensic_ids = []
    
    # Track which detectors fired to build the denominator
    detectors_seen = set()
    
    for sig in signals:
        det = sig.detector
        conf = sig.confidence
        name = sig.signal_name
        
        detectors_seen.add(det)
        
        # Metadata bookkeeping
        if name == "manifest_found" and sig.details.get("signature_valid", False):
            c2pa_verified = True
        if name in ("synthid_pattern_detected",) and conf > 0.8:
            watermark_detected = True
        if name == "ai_generator_tag_found":
            metadata_hint = True
        if name in AI_SIGNAL_NAMES and conf > 0.5:
            forensic_ids.append(name)
        
        # Only accumulate AI score for whitelist signals
        if name in AI_SIGNAL_NAMES:
            w = DETECTOR_WEIGHTS.get(det, 0.5)
            ai_score_accum += conf * w

    # The denominator is the TOTAL weight of ALL detectors in the system,
    # regardless of whether they fired. This means clean images always
    # score near 0 because their numerator is empty but denominator is full.
    total_weight = sum(DETECTOR_WEIGHTS.values())  # ~4.95

    base_probability = ai_score_accum / total_weight

    # Hard override rules
    if watermark_detected:
        base_probability = 0.99
    if c2pa_verified:
        base_probability = 0.02

    base_probability = round(min(max(base_probability, 0.0), 1.0), 4)
    confidence_score = round(min(len(detectors_seen) / len(DETECTOR_WEIGHTS), 1.0), 4)
    if watermark_detected or c2pa_verified:
        confidence_score = 0.99

    # Explanation
    explanation = "Analysis complete. "
    if base_probability > 0.65:
        explanation += "Image shows strong AI generation signatures from multiple forensic layers. "
        if watermark_detected:
            explanation += "An invisible watermark was successfully extracted. "
        if "diffusion_synthetic_noise" in forensic_ids:
            explanation += "A diffusion noise fingerprint was identified in image residuals. "
        if "deep_feature_hallucination" in forensic_ids:
            explanation += "Deep neural feature distributions show AI hallucination patterns. "
        if "synthetic_ela_and_frequency" in forensic_ids:
            explanation += "Error Level Analysis (ELA) revealed uniform synthetic compression artifacts. "
    elif base_probability < 0.25:
        explanation += "No significant AI generation artifacts found. Image appears authentic. "
        if c2pa_verified:
            explanation += "Cryptographic C2PA manifest verified as authentic. "
    else:
        explanation += f"Weak AI signals detected (score: {base_probability:.0%}). Image may be lightly post-processed. "

    return AnalysisResponse(
        ai_generated_probability=base_probability,
        confidence_score=confidence_score,
        c2pa_verified=c2pa_verified,
        watermark_detected=watermark_detected,
        metadata_ai_hint=metadata_hint,
        forensic_signals=list(set(forensic_ids)),
        explanation=explanation
    )
