#!/bin/sh

# Wait for volume to be ready (optional, usually immediate)
# sleep 5

# Run Django migrations to create/update SQLite db file in mounted volume
python manage.py migrate

# Start Gunicorn or Django server
exec gunicorn project.wsgi:application --bind 0.0.0.0:80

