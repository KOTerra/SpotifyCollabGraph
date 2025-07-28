# Use an official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Run with uvicorn (adjust path if needed)
CMD ["uvicorn", "SpotifyCollabGraph.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
