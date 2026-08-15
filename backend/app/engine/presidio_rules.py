from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from typing import Dict, Any

# Initialize Microsoft Presidio Engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scan_text_for_pii(text: str) -> Dict[str, Any]:
    """
    Scans model output text for sensitive PII leaks (Email, Credit Card, Phone, API Keys, etc.).
    """
    if not text:
        return {"has_pii": False, "detected_entities": [], "risk_score": 0.0}

    # Analyze text for PII entities
    results = analyzer.analyze(text=text, entities=[], language="en")

    detected = []
    for res in results:
        detected.append({
            "entity_type": res.entity_type,
            "start": res.start,
            "end": res.end,
            "score": res.score
        })

    has_pii = len(detected) > 0
    # Assign higher risk score if multiple or high-confidence PII found
    risk_score = 100.0 if has_pii else 0.0

    return {
        "has_pii": has_pii,
        "detected_entities": detected,
        "risk_score": risk_score
    }