# medowa-task — Apple Store-style e-commerce (Django)

A database-driven e-commerce website built with Python and Django, inspired by the concept and experience of the Apple Store. Everything on the site — products, categories, banners and orders — is managed from a purpose-built store dashboard and rendered dynamically.

## Submission

| Item | Value |
| --- | --- |
| Live Demo URL | https://medowa-task.onrender.com |
| Admin Panel URL | https://medowa-task.onrender.com/dashboard/ |
| Admin Credentials | `admin` / `Admin@12345` |
| Test User Credentials | `testuser` / `TestPass123!` |
| GitHub Repository | https://github.com/ehsaneyyy/medowa-task |

> The store dashboard at `/dashboard/` is a purpose-built control panel covering overview, products, categories, banners, orders and users (including creating, editing, disabling and deleting accounts). There is no dependency on the default Django admin.

## Technologies Used

- Python 3.11
- Django 5.2
- Tailwind CSS (Play CDN)
- Django Templates (server-rendered front end)
- Gunicorn (WSGI application server)
- WhiteNoise (static file serving in production)

## Database Used

- **PostgreSQL** in production, configured through the `DATABASE_URL` environment variable via `dj-database-url`.
- **SQLite** automatically as a fallback during local development when `DATABASE_URL` is not set.
- Database structure is defined with Django models and applied through migrations (`medowa_app/migrations/`).

## Implemented Features

1. **Homepage** — navigation/header, hero banner, featured products, product categories, promotional sections and footer. All sections are database-driven.
2. **Dynamic Banner Management** — administrators can add, edit and delete banners, upload/change banner images, update title/content, and enable/disable banners from the dashboard. Changes reflect on the site immediately.
3. **Product Management** — administrators can add, edit and delete products, upload product images, set name, description and price, assign a category, and enable/disable products. The storefront reads products dynamically from the database.
   An **admin dashboard** (staff-only, `/dashboard/`) provides a purpose-built overview with live stats plus full product, category, banner, order and user management.
4. **Product Details** — each product has its own page showing image, name, description, price, category and related product information.
5. **User Authentication** — registration, login, logout, protected account pages and a user profile page (using Django's built-in authentication).
6. **Custom Store Dashboard** — a staff-only control panel at `/dashboard/` replaces the default Django admin entirely, with overview stats plus full product, category, banner, order and user (account) management, including image uploads and order status updates.
7. **Buy Flow** — session-based shopping bag with live quantity/price updating (AJAX), checkout with shipping details, and an order confirmation page with per-user order history on the profile. Buying is customer-only: anonymous visitors are prompted to sign in, and administrator accounts have purchasing disabled.
8. **JSON API (read-only)** — endpoints exposing active products, categories and banners.

## Third-Party Libraries

| Library | Purpose |
| --- | --- |
| `django-cors-headers` | Cross-origin API access |
| `whitenoise` | Compressed static file serving in production |
| `dj-database-url` | Parse `DATABASE_URL` for database configuration |
| `python-dotenv` | Load environment variables from `.env` |
| `psycopg2-binary` | PostgreSQL driver |
| `Pillow` | Product/banner image uploads (`ImageField`) |
| `gunicorn` | Production WSGI server |

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/products/` | Active products, optional `?category=<slug>` filter |
| GET | `/api/products/<id>/` | Single active product |
| GET | `/api/categories/` | Categories with active product counts |
| GET | `/api/banners/` | Active banners |

## Project Structure

```
medowa-task/
├── manage.py
├── requirements.txt
├── build.sh                      build script (install, migrate, seed, collectstatic)
├── Procfile                      gunicorn start command
|__ render.yaml                 Render service + database definition
├── .env.example
├── medowa_task/                  project configuration (settings, urls, wsgi, asgi)
├── medowa_app/
│   ├── models.py                 Category, Product, Banner, Order, OrderItem
│   ├── views.py                  storefront, bag/checkout and API views
│   ├── dashboard_views.py        custom store dashboard views
│   ├── urls.py                   URL routes
│   ├── catalogue.py              seed catalogue data + local image path helpers
│   ├── forms.py                  registration, login, checkout and dashboard forms
│   ├── cart.py                   session-based shopping bag
│   ├── context_processors.py     injects the bag count into every template
│   ├── credentials.py            demo account definitions
│   ├── tests.py                  automated test suite
│   ├── migrations/               database migrations
│   ├── management/commands/      seed_store, make_placeholder_images, ensure_accounts, verify_accounts
│   └── templates/                front end + dashboard (base, index, product detail, cart, checkout, auth, profile, dashboard/*)
└── static/
    ├── css/app.css               custom CSS
    └── img/                      generated PNG product and banner imagery
```

## Running Locally

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py make_placeholder_images
python manage.py seed_store
python manage.py ensure_accounts
python manage.py runserver
```

Then open http://127.0.0.1:8000/ (dashboard at `/dashboard/`, `admin` / `Admin@12345`).

Run the automated test suite:

```
python manage.py test
```

## Deployment

Deployed on Render (Python runtime):

- Build command: `./build.sh`
- Start command: `gunicorn medowa_task.wsgi:application --bind 0.0.0.0:$PORT`
- Root directory: repository root
- Environment variables: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`

`build.sh` installs dependencies, applies migrations, seeds the store, provisions the admin/test accounts and collects static files.

## License / Disclaimer

medowa-task is a demonstration storefront built for a technical assessment. Product names, imagery and trademarks belong to their respective owners.
