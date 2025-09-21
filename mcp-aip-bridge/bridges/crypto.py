"""Canonical JSON + Ed25519 signing for provenance."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey, VerifyKey


def canonical_json(obj: Dict[str, Any]) -> bytes:
    """RFC 8785 canonical JSON serialization."""
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


def content_hash(msg: Dict[str, Any]) -> str:
    """Hash the canonical subset for signing."""
    subset = {
        "goal": msg.get("goal"),
        "content": msg.get("content"),
        "context": msg.get("context"),
    }
    return hashlib.sha256(canonical_json(subset)).hexdigest()


def sign_message(privkey_b64: str, msg: Dict[str, Any]) -> Dict[str, Any]:
    """Sign AIP message with Ed25519."""
    signer = SigningKey(privkey_b64, encoder=Base64Encoder)
    digest = content_hash(msg).encode()
    sig = signer.sign(digest).signature

    msg.setdefault("trust", {})["signature"] = Base64Encoder.encode(sig).decode()
    msg["trust"]["sig_key_id"] = "bridge-ed25519-v1"
    msg["trust"]["content_hash"] = content_hash(msg)

    return msg


def verify_signature(pubkey_b64: str, msg: Dict[str, Any]) -> bool:
    """Verify message signature."""
    verifier = VerifyKey(pubkey_b64, encoder=Base64Encoder)
    sig = Base64Encoder.decode(msg["trust"]["signature"])
    digest = content_hash(msg).encode()

    try:
        verifier.verify(digest, sig)
        return True
    except Exception:
        return False
