# src/webhook_app/security.py
import hmac, hashlib
from fastapi import HTTPException, Header
from .config import Cfg

def verify_signature(body: bytes, x_hub_sig_256: str | None):
    if not Cfg.GH_SECRET:
        return
    if not x_hub_sig_256:
        raise HTTPException(400, "Missing signature")
    mac = hmac.new(Cfg.GH_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    if not hmac.compare_digest(expected, x_hub_sig_256):
        raise HTTPException(401, "Invalid signature")
