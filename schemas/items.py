"""
Items schemas.
"""
from typing import Optional

from pydantic import BaseModel, Field


class Item(BaseModel):
    """Item schema."""

    name: str = Field(..., title="Item name", example="Banana")
    description: Optional[str] = Field(
        None, title="Item description", example="One pound of banana"
    )
    price: float = Field(..., title="Price of item without tax", example=4.99)
    tax: Optional[float] = Field(None, title="Tax amount", example="null")
