# Use an official Python runtime as a base image
FROM python:3.9-slim

# Install build dependencies for cryptography
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*


# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Upgrade pip and install the Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire dataset folder into the container
# COPY dataset/ ./dataset/

# Copy the rest of the code into the container
COPY . .

# Optionally, if you need to expose ports or set environment variables, you can do so here.
# For example, if your .env file holds environment variables, you'll pass it at runtime.

# Define the command to run your ETL pipeline
CMD ["python", "etl.py"]
