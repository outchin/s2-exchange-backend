#!/usr/bin/env bash
# Railway build script

set -o errexit

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
