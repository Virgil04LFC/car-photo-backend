FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer-cached unless requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
# Note: backgrounds/ image assets are not needed yet — all Phase 1 backgrounds are colour-based
# (passed via background.color param to Photoroom). Add COPY backgrounds/ when image-file
# backgrounds are introduced.

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
