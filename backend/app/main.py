import json
import os
import re
import uuid

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import root_agent
from schemas.chat import ChatRequest, ChatResponse

# ---------------------------------------------------------------------------
# ADK setup
# ---------------------------------------------------------------------------
_APP_NAME = "product_finder"
_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent,
    app_name=_APP_NAME,
    session_service=_session_service,
)

# Regex to extract the products JSON block from agent response
PRODUCTS_JSON_RE = re.compile(
    r"<PRODUCTS_JSON>\s*(.*?)\s*</PRODUCTS_JSON>", re.DOTALL
)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="Product Finder AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    user_id = "user"

    # Ensure session exists
    existing = await _session_service.get_session(
        app_name=_APP_NAME, user_id=user_id, session_id=session_id
    )
    if existing is None:
        await _session_service.create_session(
            app_name=_APP_NAME, user_id=user_id, session_id=session_id
        )

    # Build user message
    user_message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=request.query)],
    )

    # Run agent and collect final text response
    final_text = ""
    async for event in _runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(
                part.text for part in event.content.parts if part.text
            )

    # Extract products JSON block
    products: list[dict] = []
    match = PRODUCTS_JSON_RE.search(final_text)
    if match:
        try:
            products = json.loads(match.group(1))
        except json.JSONDecodeError:
            products = []
        # Remove the raw block from displayed text
        display_text = PRODUCTS_JSON_RE.sub("", final_text).strip()
    else:
        display_text = final_text.strip()

    return ChatResponse(text=display_text, products=products)
