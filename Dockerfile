# ============================================================
# PitchPerfect Dockerfile for Render Deployment
# ============================================================

# Use Python runtime with Tectonic support
FROM python:3.11-slim

# Install system dependencies including Tectonic
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://tectonic.xyz/install.sh | bash \
    && mv /usr/local/bin/tectonic /usr/bin/tectonic \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Remove tectonic from pip (we installed system version)
RUN pip uninstall -y tectonic || true

# Copy application code
COPY . .

# Create directories for Tectonic cache
RUN mkdir -p /root/.cache/Tectonic

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
