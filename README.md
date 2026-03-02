# ProductFinderAIAgent

A full-stack AI-powered product search application. Users can ask natural language questions (e.g., "Show me electronics under $200") and the system uses Google Gemini to translate them into structured filter queries against a local product catalog.

## Tech Stack

**Backend:** Python 3.10+, FastAPI, Google Gemini 2.5 Flash (via Google ADK)
**Frontend:** React 19, TypeScript, Vite

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js
- A Google API key (for Gemini)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your Google API key

# Start the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will be available at `http://localhost:5173`. The Vite dev server proxies API requests to the backend.

## API

| Method | Path      | Description                              |
| ------ | --------- | ---------------------------------------- |
| GET    | `/health` | Health check                             |
| POST   | `/chat`   | Send a natural language query, get back a text response and matching products |

### Example

**Request:**

```json
POST /chat
{
  "query": "Show me electronics under $200",
  "session_id": "some-uuid"
}
```

**Response:**

```json
{
  "text": "Here are the electronics under $200...",
  "products": [
    {
      "id": 2,
      "name": "Bluetooth Headphones",
      "category": "electronics",
      "description": "Noise-cancelling headphones.",
      "price": 199,
      "image": "https://..."
    }
  ]
}
```

## How It Works

1. The user types a natural language query in the chat interface.
2. The frontend sends the query to the `/chat` endpoint.
3. The Gemini agent interprets the query and builds a structured filter tree (supporting AND, OR, NOT with comparison operators like EQ, LT, GT, CONTAINS).
4. The filter tree is evaluated against the product catalog.
5. Matching products and a conversational response are returned to the frontend.
6. Products are displayed as cards in a grid layout.

## Testing

```bash
cd backend
pytest
```
