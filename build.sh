#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files for WhiteNoise
python manage.py collectstatic --no-input

# Run migrations against Neon PostgreSQL
python manage.py migrate

# Optional: Auto-create superuser if environment variables are set
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
    python manage.py createsuperuser --no-input || true
fi