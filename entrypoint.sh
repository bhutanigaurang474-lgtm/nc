#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z app-db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Create media directory if it doesn't exist
mkdir -p /be-app/media/profile_photos
echo "Media directory created/verified"

# Apply migrations
python manage.py migrate

# Load fixture data
python manage.py loaddata initial_data.json

# Start Django development server
exec "$@"
