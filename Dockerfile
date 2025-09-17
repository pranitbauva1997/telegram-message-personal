FROM python:3.13

# No additional system dependencies needed for bot API

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
