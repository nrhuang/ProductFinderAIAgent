# Product Finder AI Agent - Backend

A FastAPI server that uses Google's Gemini 2.5 Flash model (via Google ADK) to power a conversational product search agent. Users ask natural language questions and the agent translates them into structured filter trees to search a local product catalog.

## Prerequisites

- Python 3.10+
- A [Google API key](https://aistudio.google.com/apikey) with access to the Gemini API

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your `GOOGLE_API_KEY`.

## Running

```bash
uvicorn app.main:app --reload
```

The server starts on `http://localhost:8000` by default.

## API Endpoints

| Method | Path      | Description                              |
| ------ | --------- | ---------------------------------------- |
| GET    | `/health` | Health check                             |
| POST   | `/chat`   | Send a query and receive product results |

## Testing

```bash
pytest
```
