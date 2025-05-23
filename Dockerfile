FROM python:3.10-slim-bookworm

# Ensure all system packages are up to date to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y awscli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the rest of the application code
COPY . /app
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --upgrade accelerate
# RUN pip uninstall -y transformers accelerate
# RUN pip install transformers accelerate


# Default command to run the app
CMD ["python3", "app.py"]
