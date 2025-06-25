#  Weather Chatbot API

A FastAPI-based chatbot API that converts natural language weather queries into SQL using LlamaIndex (with Ollama), and fetches results from a TimescaleDB PostgreSQL database.



##  Features

- Token-based authentication (`Bearer` token in headers)
- Natural Language → SQL Query (via LlamaIndex)
- LLM: Local model served with Ollama (`gemma:2b`)
- Data source: TimescaleDB with weather data
- Results returned as structured JSON
- Swagger (OpenAPI) Docs at `/docs`

---

##  Requirements

Install dependencies:

```bash
pip install fastapi uvicorn sqlalchemy pandas llama-index llama-index-llms-ollama llama-index-embeddings-huggingface
```

You also need:

- Python 3.8+
- Ollama installed and `gemma:2b` pulled (`ollama pull gemma:2b`)
- PostgreSQL + TimescaleDB running with `weather_data` table

---

## Environment Setup

Update your TimescaleDB connection string in `weather_chatbot_api.py`:

```python
engine = create_engine("postgresql://tsdbuser:password123@localhost:5432/tsdb")
```

---

## Authentication

All requests require a valid Bearer token:

**Token:**

```
mysecrettoken123
```

**Header Format:**
```http
Authorization: Bearer mysecrettoken123
```

---

## Run the API

```bash
uvicorn weather_chatbot_api:app --reload
```

Open in browser:
```
http://localhost:8000/docs
```

---

## Sample Request

### cURL Example:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer mysecrettoken123" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"Compare average temperature by city\"}"
```

### JSON Request:
```json
POST /chat
Content-Type: application/json
Authorization: Bearer mysecrettoken123

{
  "question": "What is the average humidity in New York?"
}
```

### JSON Response:
```json
{
  "sql_query": "SELECT AVG(humidity) FROM weather_data WHERE city = 'New York'",
  "results": [
    {
      "avg": 64.2
    }
  ]
}





## How it Works

1. User sends natural language question.
2. App uses LlamaIndex (Ollama backend) to convert question into SQL.
3. SQL is validated, patched, and executed on TimescaleDB.
4. Query result is returned in JSON format.





