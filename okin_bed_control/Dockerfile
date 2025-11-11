# OKIN Bed BLE API Server - Docker Image
FROM python:3.11-slim

# Install bluetooth dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bluez \
    bluetooth \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy only what's needed for the server
COPY okin_bed /app/okin_bed
COPY setup.py README.md /app/

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[server]"

# Expose API port
EXPOSE 8000

# Environment variables
ENV BED_MAC_ADDRESS=""
ENV API_HOST="0.0.0.0"
ENV API_PORT="8000"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the API server
# User must provide BED_MAC_ADDRESS environment variable
ENTRYPOINT ["python", "-m", "okin_bed.api_server"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
