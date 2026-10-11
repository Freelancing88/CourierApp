#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser on deploy if ADMIN_PASSWORD is set
if [ "$ADMIN_PASSWORD" ]; then
  export DJANGO_SUPERUSER_PASSWORD="$ADMIN_PASSWORD"
  python manage.py createsuperuser --no-input --username admin --email "$ADMIN_EMAIL" || true
fi
