# medowa-task — Apple Store-Inspired Django E-commerce Storefront

A fully dynamic, database-driven storefront built with Django. Categories, products, and promotional banners are managed entirely through the Django admin, then served through server-rendered templates and a read-only JSON API that a decoupled static client can consume cross-origin.

## Live Deployment

- Live Site: https://medowa-task.onrender.com
- Admin Dashboard: https://medowa-task.onrender.com/admin/

## Verification Credentials

| Role | Username | Password | Access |
| --- | --- | --- | --- |
| Administrator | `admin` | `Admin@12345` | Django admin console at `/admin/` |
| Test Customer | `testuser` | `TestPass123!` | Authenticated profile / account page |

## Technology Stack

- Python 3.11.9
- Django 5.2.8
- Neon Serverless PostgreSQL
- Tailwind CSS Play CDN
- WhiteNoise (static asset serving)
- Gunicorn (WSGI application server)
- dj-database-url (database configuration)
- python-dotenv (environment configuration)
- django-cors-headers (cross-origin API access)
- psycopg2-binary (PostgreSQL driver)

## Core Features Summary

- Fully dynamic home grid driven entirely by the database.
- Adaptive 2-column mobile card framework that scales to 3 and 4 columns on tablet and desktop.
- Touch-swipe category navigation row.
- Persistent Neon database migration records.
- 34 automated unit validation tests.
- Active Cross-Origin Resource Sharing (CORS) header blocks for standalone static client communication.
- Django admin for full product, category, and banner CRUD, including enable/disable toggles.
- Built-in authentication: registration, login, logout, and a login-protected profile page.

## Project Structure

```
medowa-task/
├── render.yaml            # Render Blueprint (rootDir: backend)
├── backend/
│   ├── manage.py
│   ├── build.sh           # migrate -> seed_store -> ensure_accounts -> collectstatic
│   ├── requirements.txt
│   ├── medowa_task/       # project settings, urls, wsgi/asgi
│   └── medowa_app/        # models, views, urls, admin, forms, tests, templates, commands
└── frontend/              # decoupled static client (HTML/CSS/JS) consuming the JSON API
```

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/products/` | Active products, optional `?category=<slug>` filter |
| GET | `/api/products/<id>/` | Single active product |
| GET | `/api/categories/` | Categories with active product counts |
| GET | `/api/banners/` | Active banners |

## Running Locally

```
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_store
python manage.py ensure_accounts
python manage.py runserver
```

Run the automated test suite:

```
python manage.py test
```

## Database

Django ORM backed by PostgreSQL hosted on Neon. When `DATABASE_URL` is unset during local development, the project automatically falls back to a local SQLite database.

## License / Disclaimer

medowa-task is a demonstration storefront built for a technical assessment. Product names, imagery, and trademarks belong to their respective owners.
