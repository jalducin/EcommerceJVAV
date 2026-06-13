"""Verificación de firmas de webhooks entrantes.

Shopify y WooCommerce firman el cuerpo crudo con HMAC-SHA256 y lo envían en base64
en un header. La verificación se hace en tiempo constante.
"""

from __future__ import annotations

import base64
import hashlib
import hmac


def hmac_sha256_base64(secret: str, raw_body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def verify_hmac(secret: str, raw_body: bytes, provided_signature: str | None) -> bool:
    if not provided_signature:
        return False
    expected = hmac_sha256_base64(secret, raw_body)
    return hmac.compare_digest(expected, provided_signature)
