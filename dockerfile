# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . .

# Expose the port streamlit runs on
EXPOSE 8501

# Command to run the Streamlit app (will be overridden in docker-compose for the simulation script)
CMD ["streamlit", "run", "weather_chatbot.py"]
