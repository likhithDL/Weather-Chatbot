import pandas as pd
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from tqdm import tqdm
import os


CITIES = ['New York', 'Los Angeles', 'Chicago']
WEEKS = 3
PARAMETERS = {
    'temperature': (10, 35),       # °C
    'humidity': (30, 90),          # %
    'pressure': (990, 1030),       # hPa
    'wind_speed': (0, 15),         # m/s
    'precipitation': (0, 20),      # mm
    'visibility': (1, 10),         # km
    'cloud_cover': (0, 100),       # %
    'uv_index': (0, 11),           # UV Index scale
    'air_quality_index': (0, 300), # AQI
    'dew_point': (0, 25)           # °C
}
START_DATE = datetime.now() - timedelta(days=WEEKS*7)
HOURS = WEEKS * 7 * 24

rows = []
for city in tqdm(CITIES, desc="Cities"):
    for hour in range(HOURS):
        timestamp = START_DATE + timedelta(hours=hour)
        row = {'time': timestamp, 'city': city}
        for param, (low, high) in PARAMETERS.items():
            row[param] = round(random.uniform(low, high), 2)
        rows.append(row)

df = pd.DataFrame(rows)


db_user = os.getenv("POSTGRES_USER", "postgres")
db_password = os.getenv("POSTGRES_PASSWORD", "mysecret")
db_host = os.getenv("POSTGRES_HOST", "localhost")
db_port = os.getenv("POSTGRES_PORT", "5432")
db_name = os.getenv("POSTGRES_DB", "postgres")
engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")


create_table_sql = """
CREATE TABLE IF NOT EXISTS weather_data (
    time TIMESTAMP,
    city TEXT,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    wind_speed FLOAT,
    precipitation FLOAT,
    visibility FLOAT,
    cloud_cover FLOAT,
    uv_index FLOAT,
    air_quality_index FLOAT,
    dew_point FLOAT
);
"""


create_hypertable_sql = "SELECT create_hypertable('weather_data', 'time', if_not_exists => TRUE);"

with engine.connect() as conn:
    conn.execute(text(create_table_sql))
    try:
        conn.execute(text(create_hypertable_sql))
    except Exception as e:
        print(f"Could not create hypertable, likely already exists: {e}")
    conn.commit()
    
df.to_sql('weather_data', engine, if_exists='append', index=False)
print("Data inserted into TimescaleDB.")