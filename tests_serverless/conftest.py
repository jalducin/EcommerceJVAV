"""Fixtures para los tests serverless: DynamoDB mockeado con moto.

moto intercepta botocore, así que NUNCA se llega a AWS real. Se fuerzan credenciales
y región dummy por seguridad y determinismo.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from moto import mock_aws


@pytest.fixture
def aws_credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-2")


@pytest.fixture
def dynamo(aws_credentials):
    """Tabla single-table creada en un DynamoDB mockeado."""
    with mock_aws():
        from backend.db.dynamo import create_table

        create_table("metalshop")
        yield


@pytest.fixture
def client(dynamo):
    """TestClient de la app serverless con DynamoDB mockeado."""
    from backend.app import app

    with TestClient(app) as c:
        yield c
