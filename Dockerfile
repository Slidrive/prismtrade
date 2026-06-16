FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci
COPY frontend/ .
RUN npm run build
WORKDIR /app
COPY . .
EXPOSE 5000
CMD gunicorn app:app --bind 0.0.0.0:5000 --timeout 120 --workers 4
