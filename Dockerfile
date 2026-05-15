FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer-cached unless requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
# Copy background image assets (used for image_path-mode backgrounds sent to Photoroom)
COPY backgrounds/ backgrounds/

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
