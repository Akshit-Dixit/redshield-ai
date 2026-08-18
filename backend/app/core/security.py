import hmac
import hashlib
from fastapi import HTTPException, status
from app.core.config import settings

def verify_github_signature(payload_body: bytes, secret_token: str, signature_header: str) -> bool:
    """
    Validates incoming GitHub Webhook HMAC SHA-256 signature.
    """
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Hub-Signature-256 header missing."
        )

    # Extract signature algorithm and hash from header (format: sha256=hash)
    try:
        hash_type, signature = signature_header.split("=")
        if hash_type != "sha256":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported signature algorithm."
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature format."
        )

    # Compute HMAC SHA-256 digest
    mac = hmac.new(secret_token.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()

    # Secure constant-time string comparison
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid HMAC signature."
        )

    return True