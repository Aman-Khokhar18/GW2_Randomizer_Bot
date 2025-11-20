FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Environment settings for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot code
COPY . .

ENV TOKEN=""

# Default command to run the bot
CMD ["python", "bot.py"]
