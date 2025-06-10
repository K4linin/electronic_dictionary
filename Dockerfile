# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port 8000
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "electronic_dictionary.wsgi:application", "--bind", "0.0.0.0:8000"] 