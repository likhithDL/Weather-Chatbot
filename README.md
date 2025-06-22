# Weather Data Chatbot

A Streamlit-based chatbot that allows users to interact with weather data stored in a TimescaleDB (PostgreSQL) database using natural language queries. The chatbot leverages LLMs (TinyLlama via Ollama) and HuggingFace embeddings to translate user questions into SQL, visualize results, and provide insights.

## Features
- Ask natural language questions about weather data (e.g., temperature trends, humidity, city comparisons)
- Automatic SQL generation and execution
- Data visualization (tables, line charts, bar charts)
- Powered by TinyLlama (Ollama) and HuggingFace sentence-transformers
- Uses TimescaleDB for efficient time-series storage
- Includes a simulation script to generate and populate weather data

## Project Structure
- `weather_chatbot.py`: Main Streamlit app for the chatbot
- `New Python 3 week simulation script.py`: Script to generate and insert 3 weeks of weather data for multiple cities
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Multi-service setup for database, simulation, and chatbot
- `dockerfile`: Docker build instructions

## Requirements
- Python 3.9+
- Docker & Docker Compose (for containerized setup)
- Ollama (for LLM inference)

## Setup

### 1. Clone the Repository
```bash
git clone <repo-url>
cd Chatbot
```

### 2. Local Setup (Without Docker)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start a local PostgreSQL/TimescaleDB instance (or use Docker):
   - Default credentials: `postgres`/`mysecret`, DB: `postgres`
3. Run the simulation script to populate data:
   ```bash
   python "New Python 3 week simulation script.py"
   ```
4. Start the chatbot:
   ```bash
   streamlit run weather_chatbot.py
   ```

### 3. Docker Compose Setup (Recommended)
1. Ensure Docker and Docker Compose are installed.
2. Start all services:
   ```bash
   docker-compose up --build
   ```
   - This will start:
     - TimescaleDB database
     - Data simulation (runs once to populate data)
     - Streamlit chatbot (on port 8501)
3. Access the chatbot at [http://localhost:8501](http://localhost:8501)

## Usage
- Enter natural language questions (see app for examples)
- View generated SQL, results, and visualizations
- Example queries:
  - "Show temperature trend for Delhi"
  - "Compare average temperature by city"
  - "Which city had highest UV index last week?"

## Environment Variables
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`: Database connection (see `docker-compose.yml` for defaults)
- `STREAMLIT_SERVER_ADDRESS`: (Docker only) Set to `0.0.0.0` for container access

## Dependencies
- streamlit==1.31.1
- sqlalchemy==2.0.25
- pandas==2.1.4
- matplotlib==3.8.2
- llama-index==0.10.20
- llama-index-llms-ollama==0.1.4
- llama-index-embeddings-huggingface==0.1.1
- sentence-transformers==2.3.1
- psycopg2-binary==2.9.9

## Notes
- Ollama must be running and accessible for LLM inference.
- The simulation script only needs to run once to populate data (handled automatically in Docker Compose).
- The chatbot expects the weather data table schema as defined in the simulation script.

