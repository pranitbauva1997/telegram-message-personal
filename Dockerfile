FROM python:3.13

# Install libsqlite3-dev to provide libsqlite3.so.0
RUN apt-get update && apt-get install -y libsqlite3-dev && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run Functions Framework
EXPOSE $PORT
CMD functions-framework --target send_telegram_message --port $PORT
