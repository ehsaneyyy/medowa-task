#!/usr/bin/env bash
set -o errexit

echo "==> medowa-task build: start"

echo "==> Installing Python dependencies"
python -m pip install -r requirements.txt

echo "==> Applying database migrations"
python manage.py migrate --noinput

echo "==> Seeding store catalogue"
python manage.py seed_store

echo "==> Provisioning demo accounts"
python manage.py ensure_accounts

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> medowa-task build: complete"
