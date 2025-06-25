from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import pandas as pd
import re

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings

# === FastAPI App ===
app = FastAPI(title="Weather Chatbot API")

# === Auth Setup ===
VALID_TOKEN = "mysecrettoken123"  # TODO: Replace with environment variable in production
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

# === Request / Response Models ===
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql_query: str
    results: list

# === LLM & Embedding Setup ===
Settings.llm = Ollama(model="gemma:2b", request_timeout=120)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# === TimescaleDB Connection ===
engine = create_engine("postgresql://tsdbuser:password123@localhost:5432/tsdb")

# === SQL Prompt System ===
TABLE_SCHEMA = """
You are an expert SQL assistant. 
You are connected to a PostgreSQL TimescaleDB with a table named `weather_data`. The schema is:

- time (timestamp)
- city (text)
- temperature (float)
- humidity (float)
- pressure (float)
- wind_speed (float)
- precipitation (float)
- visibility (float)
- cloud_cover (float)
- uv_index (float)
- air_quality_index (float)
- dew_point (float)

ONLY return valid SQL queries using this table. Always filter by city if a city is mentioned. Never omit WHERE clauses when cities are named. Do not explain anything. If unclear, return only "INVALID".
"""

# === SQL Query Engine ===
class SQLQueryEngine:
    def __init__(self, system_prompt, llm):
        self.system_prompt = system_prompt
        self.llm = llm

    def query(self, user_question):
        full_prompt = f"{self.system_prompt}\nUser question: {user_question}"
        return self.llm.complete(full_prompt).text.strip()

query_engine = SQLQueryEngine(system_prompt=TABLE_SCHEMA, llm=Settings.llm)

# === SQL Post-Processing ===
def patch_sql_query(sql_query: str, user_input: str) -> str:
    cities_in_db = ['New York', 'Los Angeles', 'Chicago']
    for city in cities_in_db:
        if city.lower() in user_input.lower() and city not in sql_query:
            if "where" not in sql_query.lower():
                sql_query += f" WHERE city = '{city}'"
            elif "city" not in sql_query.lower():
                sql_query += f" AND city = '{city}'"
            break

    if re.search(r"\b(AVG|SUM|COUNT|MAX|MIN)\b", sql_query, re.IGNORECASE) and "GROUP BY" not in sql_query.upper():
        match = re.search(r"SELECT\s+(.*?)\s*,\s*(AVG|SUM|COUNT|MAX|MIN)\(", sql_query, re.IGNORECASE)
        if match:
            group_col = match.group(1).strip().split("AS")[0].strip()
            sql_query += f" GROUP BY {group_col}"

    column_map = {
        "timestamptask": "time",
        "click_index": "uv_index",
        "temprature": "temperature",
        "humidiity": "humidity",
        "preciptation": "precipitation"
    }
    for wrong_col, correct_col in column_map.items():
        pattern = re.compile(rf"\b{wrong_col}\b", re.IGNORECASE)
        sql_query = pattern.sub(correct_col, sql_query)

    return sql_query

# === Secured Endpoint ===
@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest, _: str = Depends(verify_token)):
    try:
        user_input = request.question
        raw_response = query_engine.query(user_input)

        match = re.search(
            r"(SELECT[\s\S]+?FROM[\s\S]+?)(WHERE[\s\S]+?|GROUP BY[\s\S]+?|ORDER BY[\s\S]+?|LIMIT[\s\S]+?|;|\n|$)",
            raw_response, re.IGNORECASE
        )
        sql_query = match.group(1).strip() if match else None

        if not sql_query or "SELECT" not in sql_query.upper():
            raise HTTPException(status_code=400, detail="Could not generate valid SQL query.")

        sql_query = patch_sql_query(sql_query, user_input)

        with engine.connect() as conn:
            df = pd.read_sql(text(sql_query), conn)

        return QueryResponse(sql_query=sql_query, results=df.to_dict(orient="records"))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
