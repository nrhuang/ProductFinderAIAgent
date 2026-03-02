from pydantic import BaseModel

from schemas.product import Product


class ChatRequest(BaseModel):
    query: str
    session_id: str = ""


class ChatResponse(BaseModel):
    text: str
    products: list[Product] = []
