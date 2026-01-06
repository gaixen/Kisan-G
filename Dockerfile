# Multi-stage Dockerfile for Kisan-G Application
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src/ ./src/
COPY public/ ./public/
COPY tsconfig.json ./
COPY craco.config.js ./
COPY tailwind.config.js ./

# Build the React app
RUN npm run build

# Stage 2: Python backend with Flask
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY server/ ./server/
COPY utils/ ./utils/
COPY RAG-gemini/ ./RAG-gemini/
COPY main.py .

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/build ./static

# Create necessary directories
RUN mkdir -p uploads logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=server/app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/api/health')"

# Run the application with gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "server.app:app", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
