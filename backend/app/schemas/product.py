from typing import Literal

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int = Field(ge=0)
    name: str = Field(min_length=1)
    category: Literal["clothing", "electronics", "accessories", "groceries"]
    description: str = Field(min_length=1)
    price: float = Field(gt=0)
    image: str = Field(min_length=1)
