FROM python:3.10-slim-bookworm

# Ensure all system packages are up to date to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project directory
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure artifacts directory exists
RUN mkdir -p /app/artifacts

# Environment variable to control whether to train during build
ENV TRAIN_ON_BUILD=false

# Pre-download models to cache them (improves startup time on hosted platforms)
RUN python3 download_models.py

# Optional: Train model during build (disabled by default for faster builds)
# Uncomment the next line if you want to train during Docker build
# RUN if [ "$TRAIN_ON_BUILD" = "true" ]; then python3 main.py; fi

# Expose port for Railway
EXPOSE $PORT

# Default command to run the app with Railway's PORT environment variable
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
