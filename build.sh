#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input

if [[ -z "${DATABASE_URL:-}" ]]; then
    echo "ERROR: DATABASE_URL is not set. Configure the Neon PostgreSQL connection on Render."
    exit 1
fi

python manage.py migrate
python manage.py populate_books

# Optional: Auto-create superuser if environment variables are set
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
    python manage.py createsuperuser --no-input || true
fi
