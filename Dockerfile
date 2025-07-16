# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.11-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ENV PYTHONPATH=/app/app

# Install pip requirements
COPY requirements.txt .

RUN python -m pip install -r requirements.txt


# Install netcat (for the wait-for-db command in docker-compose.yml)
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

# The command is defined in docker-compose.yml for better control
# CMD uvicorn main:app --host-0.0.0.0 --reload