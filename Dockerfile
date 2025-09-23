# Use a slim Python base image for smaller size
FROM python:3.9-slim-buster

# Install Graphviz - This is the critical step for the 'dot' command!
# Update apt-get, install graphviz, and clean up apt cache
RUN apt-get update -y && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy your requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your FastAPI application will listen on
# Render typically listens on port 10000, but 8000 is common for uvicorn
EXPOSE 8000

# Command to run your FastAPI application with Uvicorn
# 'main:app' refers to the 'app' object in 'main.py'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
