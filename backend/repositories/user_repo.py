"""Repositorio de usuarios (single-table DynamoDB).

Usuario: PK=USER#<id>, SK=PROFILE; lookup por email vía GSI1 (EMAIL#<email>).
Los items incluyen `hashed_password` (no se expone en la API).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key

from backend.db import keys
from backend.db.dynamo import get_table
from backend.db.serde import from_item
from backend.schemas.account import UserCreate
from backend.security import hash_password


def get_user_by_email(email: str) -> dict | None:
    resp = get_table().query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(f"EMAIL#{email.lower()}"),
    )
    items = resp.get("Items", [])
    return from_item(items[0]) if items else None


def get_user_by_id(user_id: str) -> dict | None:
    resp = get_table().get_item(Key={"PK": keys.user_pk(user_id), "SK": keys.USER_SK})
    return from_item(resp.get("Item"))


def create_user(data: UserCreate, role: str = "client") -> dict:
    """Crea un usuario. Lanza ValueError si el email ya existe."""
    if get_user_by_email(data.email):
        raise ValueError("email ya registrado")

    user_id = str(uuid.uuid4())
    item = {
        "PK": keys.user_pk(user_id),
        "SK": keys.USER_SK,
        "entity": "user",
        "id": user_id,
        "email": str(data.email).lower(),
        "full_name": data.full_name,
        "hashed_password": hash_password(data.password),
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **keys.user_gsi1(str(data.email)),
    }
    get_table().put_item(Item=item)
    return item


def public_view(user: dict) -> dict:
    """Devuelve los campos públicos del usuario (sin hash ni claves internas)."""
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "role": user.get("role", "client"),
        "is_active": user.get("is_active", True),
        "created_at": user["created_at"],
    }
