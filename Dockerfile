# Dockerfile
# Use an official Python image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false

# Create a logs directory in case nothing is mounted...
RUN mkdir /logs

# Create and set working directory
WORKDIR /app

# Copy over the pyproject.toml and poetry.lock file to install dependencies
COPY pyproject.toml poetry.lock* /app/

# Install runtime dependencies using Poetry
RUN poetry install --only main || (poetry lock --no-update && poetry install --only main)

# Copy the rest of the code
COPY . /app/

# Command to run the application
CMD ["python3", "-m", "run"]
