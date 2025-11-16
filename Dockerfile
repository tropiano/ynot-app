# Use a slim Python base image
FROM python:3.11-slim

# Environment variables for unbuffered output
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /home/app/entrypoint.sh 
RUN chmod 777 /home/app/entrypoint.sh

# Copy project files
COPY . .

# Create database directory with appropriate permissions
RUN mkdir -p /data/db && chmod 777 /data/db

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose Gunicorn port
EXPOSE 80

# Run Gunicorn WSGI server, binding to 0.0.0.0:80
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:80"]
