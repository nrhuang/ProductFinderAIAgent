from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    session_id: str = ""


class ChatResponse(BaseModel):
    text: str
    products: list[dict] = []
