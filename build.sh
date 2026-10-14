#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py seed_store
python manage.py ensure_accounts
python manage.py collectstatic --noinput
