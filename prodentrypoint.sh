#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Apply migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Load fixture data
python manage.py loaddata initial_data.json

# Start Django development server
exec "$@"
