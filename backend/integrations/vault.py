"""Vault de credenciales por conector usando AWS Secrets Manager.

Las credenciales/tokens (API keys, OAuth) nunca van en código ni en la tabla de datos.
Un secreto por conector: metalshop/connectors/<connector>.
"""

from __future__ import annotations

import json

import boto3
from botocore.exceptions import ClientError

from backend.config import settings


def _client():
    return boto3.client("secretsmanager", region_name=settings.AWS_REGION)


def _secret_name(connector: str) -> str:
    return f"metalshop/connectors/{connector}"


def put_credentials(connector: str, data: dict) -> None:
    """Crea o actualiza las credenciales del conector (idempotente)."""
    client = _client()
    name = _secret_name(connector)
    payload = json.dumps(data)
    try:
        client.create_secret(Name=name, SecretString=payload)
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ResourceExistsException":
            client.put_secret_value(SecretId=name, SecretString=payload)
        else:
            raise


def get_credentials(connector: str) -> dict | None:
    client = _client()
    try:
        resp = client.get_secret_value(SecretId=_secret_name(connector))
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ResourceNotFoundException":
            return None
        raise
    return json.loads(resp["SecretString"])
