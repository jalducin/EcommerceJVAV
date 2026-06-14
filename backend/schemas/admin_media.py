"""Schemas para gestión de categorías y subida de imágenes (panel admin)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Alta de una categoría de tienda."""

    name: str = Field(min_length=1, max_length=60)


class CategoryList(BaseModel):
    """Listado de categorías declaradas en la configuración de tienda."""

    categories: list[str]


class PresignRequest(BaseModel):
    """Solicitud de URL prefirmada para subir una imagen de producto."""

    filename: str = Field(min_length=1, max_length=200)
    content_type: str = Field(min_length=3, max_length=80)


class PresignResponse(BaseModel):
    """URL prefirmada (PUT) y URL pública resultante."""

    upload_url: str
    public_url: str
    key: str
