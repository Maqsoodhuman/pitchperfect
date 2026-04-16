# ============================================================
# PitchPerfect Dockerfile for Render Deployment
# ============================================================

# Use Python runtime with Tectonic support
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xz-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download and install Tectonic directly (v0.16.8)
WORKDIR /tmp
RUN wget https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.16.8/tectonic-0.16.8-x86_64-unknown-linux-gnu.tar.gz \
    && tar -xzf tectonic-0.16.8-x86_64-unknown-linux-gnu.tar.gz \
    && mv tectonic /usr/local/bin/ \
    && chmod +x /usr/local/bin/tectonic \
    && rm -rf tectonic-0.16.8-x86_64-unknown-linux-gnu.tar.gz

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for Tectonic cache
RUN mkdir -p /root/.cache/Tectonic

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
