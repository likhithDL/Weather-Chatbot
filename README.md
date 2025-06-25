#  Weather Data Chatbot (gemma:2b + TimescaleDB + Streamlit)

A lightweight local chatbot app that lets you query weather trends using natural language. It uses:

- **TinyLLaMA (Ollama)** as the LLM
- **TimescaleDB (PostgreSQL)** as the weather data store
- **Streamlit** for the frontend UI
- **LlamaIndex** to translate natural language into SQL

---

## Features

- Ask weather-related questions in natural language
- SQL queries are generated automatically
- Charts are displayed for trends (line, bar)
- Works completely offline using TinyLLaMA

---

## Prerequisites

- Docker + Docker Compose
- Python 3.8+
- Ollama (for running TinyLLaMA locally)
- PostgreSQL TimescaleDB enabled
- Streamlit, SQLAlchemy, llama-index, pandas, matplotlib

---

## Steps

### 1. Set up TimescaleDB with Docker

```bash
docker run -d --name timescaledb \
  -e POSTGRES_PASSWORD=mysecret \
  -p 5432:5432 \
  timescale/timescaledb:latest-pg15
```

### 2. Create the `weather_data` Table

Connect to the DB (e.g. using `psql` or PgAdmin), then run:

```sql
CREATE TABLE weather_data (
    time TIMESTAMPTZ NOT NULL,
    city TEXT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    precipitation DOUBLE PRECISION,
    visibility DOUBLE PRECISION,
    cloud_cover DOUBLE PRECISION,
    uv_index DOUBLE PRECISION,
    air_quality_index DOUBLE PRECISION,
    dew_point DOUBLE PRECISION
);

SELECT create_hypertable('weather_data', 'time');
```

### 3. Simulate & Insert Sample Data

Write a Python script to simulate 3 weeks of weather data for different cities.

### 4. Install and Run TinyLLaMA via Ollama

```bash
ollama run tinyllama
```

### 5. Create the Streamlit App

Save your script as `weather_chatbot.py`

### 6. Install Required Python Packages

```bash
pip install streamlit sqlalchemy pandas matplotlib llama-index llama-index-llms-ollama llama-index-embeddings-huggingface
```

### 7. Launch the App

```bash
streamlit run weather_chatbot.py
```

---

## Example Prompts You Can Ask

- Show temperature trend for New York
- Compare average temperature by city
- Show humidity for Chicago over time
- Which city had highest UV index last week

---

## How It Works

1. User enters a natural question.
2. LlamaIndex uses TinyLLaMA to generate SQL.
3. Streamlit displays the SQL + chart.
4. SQL runs against your TimescaleDB data.

---

## Tools Used

| Component      | Tool                      |
|----------------|---------------------------|
| LLM            | TinyLLaMA (via Ollama)    |
| Vector Engine  | LlamaIndex                |
| Embeddings     | HuggingFace MiniLM        |
| Frontend       | Streamlit                 |
| DB             | TimescaleDB (PostgreSQL)  |
| Charts         | Matplotlib                |

---

## Notes

- All models and data run locally.
- Add more prompt examples in the schema to improve results.
- If the model doesn't run as expected, consider using a larger language model like **Mistral**, **Phi-3**, etc.
