from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ExtractedItem(BaseModel):
    """Default extraction schema for articles and general web pages."""

    source_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    key_entities: list[str] = Field(default_factory=list)
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    language: Optional[str] = None
    contact_email: Optional[str] = None
    phone_numbers: list[str] = Field(default_factory=list)


class EcommerceItem(BaseModel):
    """Schema for e-commerce product extraction."""

    source_url: str
    product_name: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    availability: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sku: Optional[str] = None


SCHEMA_REGISTRY = {
    "generic": ExtractedItem,
    "default": ExtractedItem,
    "ecommerce": EcommerceItem,
}



def get_schema_model(name: str | None):
    return SCHEMA_REGISTRY.get((name or "generic").lower(), ExtractedItem)
