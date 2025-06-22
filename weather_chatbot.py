import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
import re

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings


st.set_page_config(page_title="Weather Chatbot", layout="centered")
st.title("Weather Data Chatbot (Phi-3 Mini + TimescaleDB)")


st.subheader("Ask something like:")
examples = {
    "Show temperature trend for Delhi": "Line Chart",
    "Compare average temperature by city": "Bar Chart",
    "Show humidity for Mumbai over time": "Line Chart",
    "Which city had highest UV index last week": "Ranked Table",
    "List average pressure grouped by city": "Bar Chart"
}
for q, t in examples.items():
    st.markdown(f"- `{q}` → {t}")


user_input = st.text_input("Your question:")


Settings.llm = Ollama(model="tinyllama", request_timeout=120)
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")


engine = create_engine("postgresql://postgres:mysecret@localhost:5432/postgres")


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

ONLY return valid SQL queries using this table. Do not explain anything. If unclear, return only "INVALID".

Examples:
Q: Show average temperature for New York
A: SELECT AVG(temperature) AS average_temperature FROM weather_data WHERE city = 'New York'

Q: Compare average temperature by city
A: SELECT city, AVG(temperature) AS average_temperature FROM weather_data GROUP BY city

Q: Show humidity trend in Bangalore
A: SELECT time, humidity FROM weather_data WHERE city = 'Bangalore' ORDER BY time
"""


class SQLQueryEngine:
    def __init__(self, system_prompt, llm):
        self.system_prompt = system_prompt
        self.llm = llm

    def query(self, user_question):
        full_prompt = f"{self.system_prompt}\nUser question: {user_question}"
        return self.llm.complete(full_prompt).text.strip()

query_engine = SQLQueryEngine(system_prompt=TABLE_SCHEMA, llm=Settings.llm)


if user_input:
    with st.spinner("Thinking..."):
        try:
            response_text = query_engine.query(user_input)

            
            match = re.search(r"(SELECT[\s\S]+?FROM[\s\S]+?)(WHERE[\s\S]+?|GROUP BY[\s\S]+?|ORDER BY[\s\S]+?|LIMIT[\s\S]+?|;|\n|$)", response_text, re.IGNORECASE)
            sql_query = match.group(1).strip() if match else None

            
            if sql_query:
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

            
            st.markdown("**LLM-generated SQL:**")
            st.code(sql_query or "No SQL found", language="sql")

            
            if sql_query and "select" in sql_query.lower():
                with engine.connect() as conn:
                    preview_row = conn.execute(text("SELECT * FROM weather_data LIMIT 1")).fetchone()
                    if preview_row:
                        st.caption(f"Available columns: {', '.join(preview_row._mapping.keys())}")

                    df = pd.read_sql(text(sql_query), conn)

                if df.empty:
                    st.warning("Query executed, but returned no results.")
                else:
                    st.dataframe(df)
                    if 'time' in df.columns and df.shape[1] >= 2:
                        fig, ax = plt.subplots()
                        for col in df.columns:
                            if col not in ['time', 'city']:
                                ax.plot(df['time'], df[col], label=col)
                        ax.set_xlabel("Time")
                        ax.set_ylabel("Value")
                        ax.set_title("Time Series Chart")
                        ax.legend()
                        st.pyplot(fig)
            else:
                st.warning("No valid SQL query found. Try rephrasing your question.")

        except Exception as e:
            st.error(f"Error: {e}")
