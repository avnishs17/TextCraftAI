FROM python:3.10-slim-bookworm

# Ensure all system packages are up to date to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y awscli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ /app/src/
COPY config/ /app/config/
COPY params.yaml /app/
COPY app.py /app/
COPY main.py /app/
COPY setup.py /app/
COPY templates/ /app/templates/
COPY static/ /app/static/

# Copy trained model artifacts (if they exist) - create empty directory if not
RUN mkdir -p /app/artifacts

# Environment variable to control whether to train during build
ENV TRAIN_ON_BUILD=false

# Pre-download the base model to cache it
RUN python3 -c "from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; AutoTokenizer.from_pretrained('google/pegasus-cnn_dailymail'); AutoModelForSeq2SeqLM.from_pretrained('google/pegasus-cnn_dailymail')" || echo "Model download failed, will download at runtime"

# Optional: Train model during build (disabled by default for faster builds)
# Uncomment the next line if you want to train during Docker build
# RUN if [ "$TRAIN_ON_BUILD" = "true" ]; then python3 main.py; fi

# Default command to run the app
CMD ["python3", "app.py"]
