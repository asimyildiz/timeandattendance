FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose default port for FastAPI
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]