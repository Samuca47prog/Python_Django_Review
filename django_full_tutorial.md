
# Python Django Full Tutorial (Windows, Web + API)

Awesome — let’s do a compact but end-to-end Django refresher tailored for Windows, focusing on solid patterns and production-minded defaults. We’ll build a minimal “shop” project with a `products` app and show web + API (Django REST Framework). You can paste each snippet as-is.

---

## 0) Prereqs & Setup (Windows)

**Install (recommended):**
- Python 3.11+ (enable “Add Python to PATH”)
- Git
- (Optional but great) WSL2 + Ubuntu for a Linux-like prod parity
- A code editor (VS Code)

### Default
**Create project folder & venv**
```powershell
mkdir django-shop && cd django-shop
python -m venv .venv
. .\.venv\Scripts\Activate.ps1           # PowerShell
python -m pip install --upgrade pip
pip install "django>=5.0,<6.0" psycopg2-binary python-dotenv djangorestframework
```

**Start project & app**
```powershell
django-admin startproject config .
python manage.py startapp products
```

### Option with UV
> Install uv once (e.g., via pipx install uv or the official installer). After that, per-project:

```
# 0. Create project directory
mkdir django-shop; cd django-shop

# 1. Initialize a project with pyproject.toml + lockfile
uv init  # creates pyproject.toml

# 2. (Optional) create a dedicated .venv
uv venv --seed  # makes .venv in the project

# 3. Add dependencies (pinned in lockfile)
uv add "django>=5,<6" psycopg2-binary python-dotenv djangorestframework

# 4. Start project & app (all inside the env)
uv run django-admin startproject config .
uv run python manage.py startapp products

# 5. Run dev server
uv run python manage.py migrate
uv run python manage.py runserver

```

Why this is nice
* uv add updates pyproject.toml and lockfile atomically.
* uv run ensures the command runs in the right environment without activating.
* uv venv keeps a local .venv so editors (VS Code) auto-detect it.
  
### Option with Poetry
> Install Poetry once (best via pipx install poetry). Then:

```
# 0. Create project directory
mkdir django-shop; cd django-shop

# 1. Initialize the project (non-interactive)
poetry init -n

# 2. Configure Poetry to create the venv inside the project (nice on Windows)
poetry config virtualenvs.in-project true

# 3. Add dependencies (creates poetry.lock)
poetry add "django@^5" psycopg2-binary python-dotenv djangorestframework

# 4. Spawn a shell in the venv (or use `poetry run ...`)
poetry shell

# 5. Start project & app
django-admin startproject config .
python manage.py startapp products

# 6. Run dev server
python manage.py migrate
python manage.py runserver
```



### **Project layout (goal)**
```
django-shop/
  .env
  .venv/
  config/
    __init__.py
    settings.py
    urls.py
    wsgi.py
    asgi.py
  products/
    __init__.py
    admin.py
    apps.py
    models.py
    views.py
    urls.py
    forms.py
    signals.py
    serializers.py
    tests/
  templates/
    base.html
    products/
      product_list.html
      product_detail.html
      product_form.html
      product_confirm_delete.html
  static/
    css/app.css
  manage.py
```

### Congig files

#### asgi.py

What it is: The ASGI entrypoint (Async Server Gateway Interface). If you run Django with an ASGI server (e.g., uvicorn, daphne, hypercorn) for WebSockets/long-lived connections or just modern async HTTP, this file exposes the application callable the server imports.

Default shape (Django creates this):
```python
# config/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
```

How it works:
* Sets DJANGO_SETTINGS_MODULE (same as manage.py and wsgi.py). 
* Builds an ASGI application using your settings (middleware, URL routing, etc. still live in settings.py/urls.py).

When you touch it:
* When adding Channels or other ASGI routers/middleware. Example (conceptual):

```python
# config/asgi.py with Channels
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()
websocket_urlpatterns = [
    path("ws/echo/", ...),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(websocket_urlpatterns),
})
```
* When mounting third-party ASGI apps (e.g., Starlette subapps) side-by-side.
* 
Common gotchas:
* Don’t put heavy DB calls here; the server imports this on startup.
* If you enable ASGI middleware (like WhiteNoise’s ASGI integration), ensure ordering matches docs and settings (usually you still prefer WhiteNoise via Django middleware in settings.py).


#### wsgi.py

What it is: The WSGI entrypoint (classic sync interface). If you deploy with gunicorn, uWSGI, or mod_wsgi you point them to this file’s application.

Default:
```python
# config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

When to use WSGI vs ASGI:
* WSGI: perfectly fine for plain HTTP apps; simplest, battle-tested.
* ASGI: needed for WebSockets, HTTP/2 push, or to leverage Django’s async views stack end-to-end.

Common tweaks:
* Historically WhiteNoise wrapped WSGI here; nowadays the recommended approach is middleware in settings.py (see below), which works for both dev & prod.


#### settings.py

What it is: The single source of truth for Django config. Everything else (manage.py/asgi/wsgi) just sets DJANGO_SETTINGS_MODULE and loads this.

[settings docs](https://docs.djangoproject.com/en/5.2/topics/settings/)

Default:
```python
"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-1=nu57$ohuaw2wu!*e1fle-h=57@q9f6l3**szfwifsr-dajpr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

Typical skeleton with sensible, env-driven bits:

**.env (local development)**
```ini
DEBUG=True
SECRET_KEY=dev-secret-CHANGE_ME
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

**settings.py**
```python
# config/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # so .env vars are available in dev

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Core security/env ---
SECRET_KEY = os.getenv("SECRET_KEY", "insecure")        # set in production
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS","").split(",") if o.strip()]

# --- Applications ---
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd-party
    "rest_framework",

    # Your apps
    "products.apps.ProductsConfig",
]

# --- Middleware (order matters) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise (if used) should be just under SecurityMiddleware:
    # "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# --- Templates ---
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],  # your global templates dir
    "APP_DIRS": True,                  # also load app/templates/** automatically
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ],
    },
}]

# --- Gateways (entrypoints) ---
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# --- Database (SQLite dev; configure Postgres for prod) ---
if os.getenv("DATABASE_URL"):
    # optional: dj-database-url; otherwise parse manually
    import dj_database_url
    DATABASES = {"default": dj_database_url.parse(os.getenv("DATABASE_URL"), conn_max_age=600)}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

# --- Auth/Users/Passwords ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n/time ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --- Static & Media ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]           # dev-only assets you author
STATIC_ROOT = BASE_DIR / "staticfiles"             # collectstatic output (prod)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"                    # user uploads (serve via web server in prod)

# Enable hashed/compressed static (if using WhiteNoise)
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- DRF example defaults ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # e.g. JWT if you add simplejwt:
        # "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Logging to console (prod-safe baseline) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}
```
Run initial migration and dev server:
```powershell
python manage.py migrate
python manage.py runserver
```

Key relationships:
* ROOT_URLCONF points to config.urls (explained next).
* WSGI_APPLICATION/ASGI_APPLICATION point to the callables in wsgi/asgi.
* INSTALLED_APPS must include your apps (e.g., products.apps.ProductsConfig) or the app won’t load models, admin, signals, templates, or static discovery.

Common production flags to also set via env:
```python
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False") == "True"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # once HTTPS is proven correct
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

Typical pitfalls:
* ALLOWED_HOSTS empty in prod → Django returns 400 (Bad Request).
* CSRF_TRUSTED_ORIGINS missing when you first put HTTPS behind a proxy → 403 CSRF failures.
* STATIC_ROOT not set → collectstatic does nothing; prod can’t serve assets.
* Adding an app but forgetting to put it in INSTALLED_APPS → admin/models/templates not discovered.
* APP_DIRS=True missing → templates under app/templates/ aren’t picked up.

#### urls.py

What it is: The project-level URL router. It maps URL patterns to views or delegates to app routers.

Typical structure:
```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("products.urls", namespace="products")),  # web UI
    path("api/", include("products.urls_api")),                # DRF router
]

# In DEBUG, serve media files via Django (OK for local dev)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

Notes:
* Use include() to delegate to each app’s urls.py. Keeps the project router clean.
* Namespacing (app_name in the app’s urls.py) prevents URL name collisions.
* For DRF, you often use a router (DefaultRouter) in products/urls_api.py.

Common pitfalls:
* Missing trailing slash patterns vs APPEND_SLASH behavior (Django will redirect if enabled).
* Static/media serving in production should be done by WhiteNoise/Nginx/Cloud—not via static() helper; that block should be guarded by if settings.DEBUG: only.

### How these four play together (one mental picture)

1. Server starts:
   1. ASGI server imports config.asgi:application or WSGI server imports config.wsgi:application.
2. asgi/wsgi.py set DJANGO_SETTINGS_MODULE and build the Django application.
3. settings.py loads, defining installed apps, middleware, and ROOT_URLCONF.
4. urls.py exposes urlpatterns which tie requests to views; Django resolves and dispatches.
   1. > manage.py and many Django internals do the same dance: set DJANGO_SETTINGS_MODULE, import settings, then bootstrap apps and URLs.

### Quick “what do I change where?” cheat-sheet

* Add a new app → INSTALLED_APPS in settings.py.
* Add middleware → MIDDLEWARE in settings.py (ordering matters).
* Add URL endpoints → urls.py (project) and app/urls.py (app).
* Switch DB to Postgres → DATABASES in settings.py` (env-driven).
* Enable WebSockets → replace/extend asgi.py with Channels ProtocolTypeRouter.
* Production hardening → toggles in settings.py (secure cookies, HSTS, SSL redirect, logging), rarely touch asgi/wsgi.



### Create super user

0) Pre-check (one time)

Make sure migrations ran and the admin app is enabled:
```powershell
# If you’ve not done this since creating the project:
poetry run python manage.py migrate
```

In config/settings.py make sure:
```python
INSTALLED_APPS = [
    # ...
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

1) Interactive (fastest)

Runs a prompt for username/email/password:
```powershell
poetry run python manage.py createsuperuser
```
Follow the prompts, then log in at:
```arduino
http://127.0.0.1:8000/admin/
```

2) Non-interactive (great for CI/Docker)

Use the environment variables Django reads when --noinput is used:
```powershell
# PowerShell: set for this process only
$env:DJANGO_SUPERUSER_USERNAME = "admin"
$env:DJANGO_SUPERUSER_EMAIL    = "admin@example.com"
$env:DJANGO_SUPERUSER_PASSWORD = "S0meLong#Password"

poetry run python manage.py createsuperuser --noinput
```
> Notes
> * Password must meet your validators (see  AUTH_PASSWORD_VALIDATORS in settings).
> * In CI, set these env vars in the pipeline/secret store rather than hard-coding them.
---

## 1) Apps

### What is an “app” in Django?
* A **unit of functionality** (models, admin, views, templates, signals…).
* Each app has an AppConfig class that Django loads and then calls ready() on after the app registry is fully populated. That’s the right place to wire signals, checks, etc.

### The correct setup for Django 5.x

1) `products/apps.py` (use AppConfig)
```python
# products/apps.py
from django.apps import AppConfig

class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # good default for new apps
    name = "products"           # dotted path of the app package
    verbose_name = "Products"   # optional: nicer name in admin

    def ready(self) -> None:
        # Import modules that register side-effects (signals, system checks, etc.)
        import products.signals  # noqa: F401
```

2) `config/settings.py` (reference the config class)
```python
INSTALLED_APPS = [
    # Django contrib apps...
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third-party...
    # "rest_framework",

    # your apps:
    "products.apps.ProductsConfig",   # ✅ explicit AppConfig reference
]
```

### Signals — how to wire them safely
`products/signals.py`
```python
from django.db.models.signals import pre_save, post_migrate
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product

@receiver(pre_save, sender=Product, dispatch_uid="products.product_slug_auto")
def product_slug_auto(sender, instance: Product, **kwargs):
    if not instance.slug and instance.name:
        instance.slug = slugify(instance.name)

@receiver(post_migrate, dispatch_uid="products.seed_defaults")
def seed_defaults(sender, app_config, **kwargs):
    # Example: create a default product after migrations (idempotent)
    if app_config.name != "products":
        return
    Product.objects.get_or_create(
        name="Keyboard",
        defaults={"price": 199.90, "is_active": True},
    )
```
Why this pattern works:
* Importing products.signals inside AppConfig.ready() ensures the app registry is ready (avoids circular imports/partial model states).
* dispatch_uid makes handler registration idempotent (prevents duplicates under the dev autoreloader or multi-worker setups).

### Common pitfalls & fixes
* Using `default_app_config`: remove it (Django ≥3.2 doesn’t need it; Django 5 has dropped it).
* Importing signals at module import time (e.g., in products/__init__.py) can cause circular-import issues. Always do it in ready().
* Duplicate signal execution in dev: add dispatch_uid to @receiver (or use explicit signal.connect(..., dispatch_uid=...)).
* Cross-app model references in signals: to avoid import cycles, resolve lazily:
```python
  from django.apps import apps
  Order = apps.get_model("orders", "Order")  # app_label, ModelName
```
* Doing heavy work in ready() (DB/network): avoid—use post_migrate, a startup management command, or a background task.


### How to create a page
Easy. Here are two clean ways—pick one:
* A) Truly static page (no DB query) using TemplateView
* B) Dynamic page (list products) using a small view

I’ll also show the minimal HTML and CSS and where to put each file.


0) Project router delegates correctly?
Open `config/urls.py` and make sure it includes your app routes at the root:
```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # ⬇️ this puts products' routes at the site root, so /about/ works
    path("products/", include(("products.urls", "products"), namespace="products")),
]
```

#### A) Static “About Products” page (TemplateView)

1) Route
`products/urls.py`
```python
from django.urls import path
from django.views.generic import TemplateView

app_name = "products"

urlpatterns = [
    # ... your existing routes
    path("about/", TemplateView.as_view(template_name="products/about.html"), name="about"),
]
```

2) Template
`templates/products/about.html`
```html
{% load static %}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>About Products</title>
  <link rel="stylesheet" href="{% static 'css/products.css' %}">
</head>
<body>
  <header><h1>About Our Products</h1></header>
  <main class="container">
    <p>This is a simple static page with a tiny CSS file.</p>
    <ul class="bullets">
      <li>Quality items</li>
      <li>Fair pricing</li>
      <li>Fast delivery</li>
    </ul>
  </main>
</body>
</html>
```

3) CSS
`static/css/products.css`
```css
html, body { margin: 0; padding: 0; font-family: system-ui, Arial, sans-serif; }
header { padding: 16px; border-bottom: 1px solid #ddd; }
.container { max-width: 720px; margin: 24px auto; padding: 0 16px; line-height: 1.6; }
.bullets { margin: 12px 0; }
```

ready to open `http://127.0.0.1:8000/products/about/`


#### B) Dynamic “About Products” page (list products)

1) View
`products/views.py`
```python
from django.shortcuts import render

def about_products(request):
    products = []
    return render(request, "products/about.html", {"products": products})
```

2) Route
`products/urls.py`
```python
from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    # ... your existing routes
    path("about/", views.about_products, name="about"),
]
```

### Recommended layering inside an app
```graphql
products/
  __init__.py
  apps.py
  models.py
  managers.py          # custom QuerySet/Manager (optional but great)
  selectors.py         # READ-ONLY query helpers (no side-effects)
  services.py          # WRITE/side-effect operations (create/update/delete)
  validators.py        # app-specific validation (if needed)
  forms.py             # HTML forms (server-side validation/UI)
  serializers.py       # DRF serializers (API validation)
  views.py             # calls selectors/services + handles HTTP
  urls.py
  signals.py
  tests/
```
* selectors.py: “Which data to read?” Pre-optimized queries, NO writes. Safe to cache.
* services.py: “What change to make?” Transactional business operations.
* managers.py: Custom QuerySet/Manager methods to encapsulate common filters.
* views.py: Glue only—parse input → call selector/service → render/redirect/JSON.
This separation makes unit testing trivial and prevents fat views.

#### 1) Model + Manager/QuerySet (optional but powerful)
`models.py`
```python
from django.db import models

class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

class Product(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
```
> Now you can do `Product.objects.active()` anywhere (selectors/services/views/tests).

#### 2) selectors.py (read-only logic)
```python
# products/selectors.py
from django.db.models import QuerySet
from .models import Product

def list_products(q: str | None = None, active_only: bool = True) -> QuerySet[Product]:
    qs = Product.objects.all()
    if active_only:
        qs = qs.active()
    if q:
        qs = qs.filter(name__icontains=q)
    return qs.select_related()  # add select_related/prefetch_related as needed

def get_product_by_slug(slug: str) -> Product:
    return Product.objects.get(slug=slug)
```
> Rules of thumb: **no writes**, no transactions here. Just consistent, optimized queries.

#### 3) services.py (write/side-effect logic)
```python
# products/services.py
from django.db import transaction
from django.db.models import F
from django.utils.text import slugify
from .models import Product

@transaction.atomic
def create_product(*, name: str, description: str = "", price: float = 0.0, is_active: bool = True) -> Product:
    slug = slugify(name)
    obj = Product.objects.create(
        name=name, slug=slug, description=description, price=price, is_active=is_active
    )
    return obj

@transaction.atomic
def update_product_price(*, product_id: int, new_price: float) -> Product:
    # safe concurrent update
    Product.objects.filter(pk=product_id).update(price=new_price)
    return Product.objects.get(pk=product_id)

@transaction.atomic
def deactivate_product(*, slug: str) -> None:
    p = Product.objects.select_for_update().get(slug=slug)
    p.is_active = False
    p.save(update_fields=["is_active"])
```
> Put business invariants here (e.g., “price cannot be negative”) and raise domain errors. Views should not duplicate this logic.

#### 4) Use them in views

##### A) Function-Based Views (FBV)
```python
# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from . import selectors, services
from .forms import ProductForm

def product_list(request):
    q = request.GET.get("q")
    products = selectors.list_products(q=q)
    return render(request, "products/product_list.html", {"products": products})

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            services.create_product(**form.cleaned_data)
            return redirect("products:list")
    else:
        form = ProductForm()
    return render(request, "products/product_form.html", {"form": form})

def product_deactivate(request, slug):
    # permission checks here if needed
    services.deactivate_product(slug=slug)
    return redirect("products:list")
```

##### B) Class-Based Views (CBV)
```python
# products/views.py
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from . import selectors, services
from .forms import ProductForm

class ProductListView(ListView):
    template_name = "products/product_list.html"
    paginate_by = 10

    def get_queryset(self):
        q = self.request.GET.get("q")
        return selectors.list_products(q=q)

class ProductCreateView(CreateView):
    form_class = ProductForm
    template_name = "products/product_form.html"
    success_url = reverse_lazy("products:list")

    def form_valid(self, form):
        services.create_product(**form.cleaned_data)
        return super().form_valid(form)  # or redirect yourself
```
> For **UpdateView/DeleteView**, override form_valid()/delete() and call your service.

#### 5) Validation: where?

* HTML views: use `forms.py` (ModelForm/Form) as the primary validation + UI binding.
* APIs (DRF): use serializers for validation; call services in `Serializer.create/update` or in `ViewSet.perform_create/perform_update`.
* Services assume validated inputs (DTO pattern). They enforce business rules, not raw parsing.

Example DRF create using services:
```python
# products/serializers.py
from rest_framework import serializers
from .models import Product
from . import services

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "price", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def create(self, validated_data):
        return services.create_product(**validated_data)
```

#### 6) Where to put tiny helpers?

* Pure helpers (formatting, math): utils.py (no Django imports).
* Cross-app stuff: a “core” app with core/services.py, core/selectors.py.
* Long-running / async work: tasks.py and Celery (services enqueue tasks, tasks call services).

#### 7) Concurrency & transactions (must-know)

* Wrap multi-write operations with @transaction.atomic.
* Use select_for_update() to lock rows when enforcing invariants.
* Use F expressions for atomic increments/decrements.
* Keep transactions short; do not call external services inside them.

#### 8) Testing strategy

Unit test services/selectors directly (fast, no HTTP client needed).

View tests should be thin: focus on routing/permissions/template context.

Example:
```python
# products/tests/test_services.py
import pytest
from products import services

@pytest.mark.django_db
def test_create_product_sets_slug():
    p = services.create_product(name="My Keyboard", price=100)
    assert p.slug.startswith("my-keyboard")
```

#### TL;DR

* Put reads in selectors.py, writes in services.py, and keep views thin.
* Use QuerySet/Manager methods for reusable filters.
* Validate via forms (HTML) or serializers (API), and enforce domain rules in services.
* Call your functions from FBVs/CBVs/DRF views with a few lines of glue.


---

## 2) Models

`products/models.py`
```python
from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
```

Optimized models.py
```python
# products/models.py
from __future__ import annotations
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.db.models import Q, F
from django.urls import reverse

class Product(models.Model):
    name = models.CharField(max_length=120, unique=True) 
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)  # set on INSERT
    updated_at = models.DateTimeField(auto_now=True)      # set on UPDATE

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"], name="product_slug_idx"),
            models.Index(fields=["-created_at"], name="product_created_idx"),
        ]
        constraints = [
            # Example: ensure non-negative price (also enforced by validator)
            models.CheckConstraint(check=Q(price__gte=0), name="product_price_gte_0"),
        ]

    def __str__(self) -> str:
        return self.name

    # Optional: auto-slug if blank (you can also do this in a pre_save signal)
    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base = slugify(self.name)
            slug = base
            i = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        return super().save(*args, **kwargs)

    # URLs for convenience in templates/views
    def get_absolute_url(self) -> str:
        return reverse("products:detail", kwargs={"slug": self.slug})

    def publish(self):
        """Example domain method."""
        if self.published_at is None:
            self.published_at = timezone.now()
            self.save(update_fields=["published_at", "updated_at"])
```
### A. Registering a model in Admin
for the model to appear in Admin section, it must be added to the admin file

`products/admin.py`
```python
from .models import Product

admin.site.register(Product)
```

### B. Relationships

#### 1) One-to-Many: Category → Product
* Each product belongs to a category; categories list their products.
* Use PROTECT to prevent deleting a category that still has products.

```python
class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Product(models.Model):
    # ... previous fields ...
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True, blank=True,
    )
    # rest of Product as above
```

usage
```python
# create
c = Category.objects.create(name="Keyboards", slug="keyboards")
p = Product.objects.create(name="MX Board", price=Decimal("299.00"), category=c)

# reverse relation
c.products.all()      # QuerySet[Product]
p.category.name
```

#### 2) One-to-One: Product ↔ Detail
* Split rarely-needed columns into a different table.
```python
class ProductDetail(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="detail"
    )
    specs_json = models.JSONField(default=dict, blank=True)

```

usage
```python
p.detail.specs_json  # raises ProductDetail.DoesNotExist if not created yet
```

#### 3) Many-to-Many: Product ↔ Tag (with and without “through”)
* Simple M2M:
```python
class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)
    def __str__(self): return self.name

class Product(models.Model):
    # ...
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)
```

usage
```python
t = Tag.objects.create(name="mechanical")
p.tags.add(t)
p.tags.all()          # tags for a product
t.products.all()      # products for a tag
```

* M2M with extra fields (custom “through” model):
```python
class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField(default=1)
    class Meta:
        unique_together = [("product", "tag")]

class Product(models.Model):
    # ...
    tags = models.ManyToManyField(Tag, through="ProductTag", related_name="products")
```

#### 4) One-to-Many: Product → ProductImage
* Store multiple images per product.
```python
# pip install Pillow
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/%Y/%m/")  # MEDIA_ROOT required
    alt = models.CharField(max_length=120, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]
        indexes = [models.Index(fields=["product", "position"])]
```

### C. Useful model methods & patterns

#### 1) Choices with enums (nice admin + get_FOO_display())
```python
class ProductStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"

class Product(models.Model):
    # ...
    status = models.CharField(
        max_length=16, choices=ProductStatus.choices, default=ProductStatus.DRAFT
    )

# Usage
p.get_status_display()        # "Draft", "Published", ...
```


#### 2) Validation hooks: clean() and full_clean()
```python
from django.core.exceptions import ValidationError

class Product(models.Model):
    # ...
    def clean(self):
        super().clean()
        if self.price and self.price > Decimal("100000.00"):
            raise ValidationError({"price": "Price too large for this catalog."})
```
> Django forms/ModelForms call `full_clean()`. If you create models directly, call obj.full_clean() before save() when you want model-level validation enforced.

#### 3) update_fields to speed up writes
```python
p.name = "New name"
p.save(update_fields=["name", "updated_at"])
```

#### 4) refresh_from_db to re-load after concurrent updates
```python
p.refresh_from_db(fields=["price"])
```

#### 5) Soft-delete pattern (conditional uniqueness)
If you soft-delete or mark inactive, you often want unique constraints only for active rows:
```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["slug"],
            condition=Q(is_active=True),
            name="uniq_active_slug"
        )
    ]
```

### D. Managers & QuerySets (useful functions you’ll call from views/services)
Put read filters in a custom QuerySet and expose via manager:
```python
class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def search(self, q: str | None):
        return self if not q else self.filter(name__icontains=q)

    def published(self):
        return self.filter(status="published")

class Product(models.Model):
    # ...
    objects = ProductQuerySet.as_manager()
```

usage
```python
Product.objects.active().search("keyboard").order_by("price")
Product.objects.select_related("category").prefetch_related("tags")
```

> Tips:
> * select_related() for FK/OneToOne (joins, single query).
> * prefetch_related() for M2M/Reverse FK (two queries + in-Python join).
> * only()/defer() to trim columns when listing.


### E. Constraints, indexes, performance
* UniqueConstraint with Lower() (case-insensitive uniqueness, PostgreSQL):
```python
from django.db.models.functions import Lower
models.UniqueConstraint(Lower("name"), name="uniq_product_name_ci")
```
* CheckConstraint for domain rules (price ≥ 0 shown above).
* GIN/JSON indexes (Postgres) for JSONField searches if you store specs.
* Always index fields used in filters/joins/sorting often (slug, FK, created_at).

### F. Common ORM operations you’ll use
```python
from django.db import transaction
from django.db.models import Count, Sum, Avg, F, Q

# get_or_create / update_or_create
p, created = Product.objects.get_or_create(name="Keyboard", defaults={"price": 199.90})
obj, _ = Product.objects.update_or_create(slug="mx-board", defaults={"price": 249.00})

# annotate / aggregate
Product.objects.active().annotate(tag_count=Count("tags")).order_by("-tag_count")
Product.objects.aggregate(avg_price=Avg("price"))

# transactions
with transaction.atomic():
    Product.objects.filter(pk=p.pk).update(price=F("price") - 10)

# bulk ops
Product.objects.bulk_create([
    Product(name="Mouse", price=Decimal("99.90")),
    Product(name="Monitor", price=Decimal("999.00")),
])
```

### G. Files/media note
If you use ImageField/FileField, configure:
```python
# settings.py
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

Serve via Django only in dev:

```python
# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
In prod, serve media via your web server or object storage (S3, etc.).

### TL;DR

* Model relationships: FK (Category), O2O (Detail), M2M (Tag), reverse managers.
* Add indexes; use select_related/prefetch_related.
* Keep business logic in model methods/managers (plus your services.py layer).
* Use constraints (Check/Unique with conditions) to move invariants to the DB.


### Migrations

#### What a migration is
* **Schema migration**: describes changes to tables/indexes/constraints (add/rename fields, create models, add indexes…).
* **Data migration**: Python code that transforms data (backfills a new column, moves data between fields, etc.).
* Each migration is a Python file in app_name/migrations/, named like 0003_add_status.py, and forms a graph with dependencies.

Typical workflow:
```powershell
# after editing models.py
poetry run python manage.py makemigrations products
poetry run python manage.py migrate              # applies to DB
poetry run python manage.py showmigrations       # see status
poetry run python manage.py sqlmigrate products 0003  # preview SQL
```
> Use --name to label a migration:
> `poetry run python manage.py makemigrations products --name add_status_to_product`

#### Reading a migration file
A minimal “create model” migration looks like:
```python
# products/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []  # runs first for this app
    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120, unique=True)),
                ("slug", models.SlugField(max_length=140, unique=True, blank=True)),
                ("price", models.DecimalField(max_digits=10, decimal_places=2, default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
```
* dependencies controls ordering across apps.
* operations is an ordered list of atomic steps (create/alter/rename/constraints/indexes).

#### Common schema operations (copy/paste)

##### Add a new nullable column (safe default)
```python
migrations.AddField(
    model_name="product",
    name="status",
    field=models.CharField(max_length=16, null=True, blank=True),
)
```

##### Make it NOT NULL after backfilling (two-step)
```python
migrations.AlterField(
    model_name="product",
    name="status",
    field=models.CharField(max_length=16, null=False, default="draft"),
)
```

##### Rename a field (preserves data)
```python
migrations.RenameField("product", "old_name", "name")
```

##### Add/Remove unique constraint or index
```python
from django.db.models import Q, Index
migrations.AddConstraint(
    model_name="product",
    constraint=models.UniqueConstraint(
        fields=["slug"], condition=Q(is_active=True), name="uniq_active_slug"
    ),
)
migrations.AddIndex(
    model_name="product",
    index=Index(fields=["-created_at"], name="product_created_idx"),
)
```

##### Add a ForeignKey / ManyToMany
```python
migrations.AddField(
    model_name="product",
    name="category",
    field=models.ForeignKey(
        to="products.category", on_delete=models.PROTECT, null=True, blank=True, related_name="products"
    ),
)
```

#### Data migrations (RunPython): backfill safely
Use historical models via apps.get_model() (not direct imports), so the migration works even after models change later.

```python
# products/migrations/0005_backfill_status.py
from django.db import migrations

def forward(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    # bulk update without loading all rows into memory
    Product.objects.filter(status__isnull=True).update(status="draft")

def backward(apps, schema_editor):
    Product = apps.get_model("products", "Product")
    Product.objects.filter(status="draft").update(status=None)

class Migration(migrations.Migration):
    dependencies = [("products", "0004_add_status")]
    operations = [migrations.RunPython(forward, backward)]
```
> Important: Put data migrations in a separate migration right after the schema change. Keep functions idempotent where possible.

#### Zero-downtime pattern for “NOT NULL + default” on big tables (prod)
1. Add nullable column (no default at DB-level):
```python
migrations.AddField(... null=True, blank=True)
```
2. Deploy this; app writes new rows with value, old rows remain NULL.
3. Backfill with a RunPython migration in batches (if very large, do it offline/management command).
4. Enforce NOT NULL and add default (application-level default is fine, DB-level default optional):
```python
migrations.AlterField(... null=False, default="draft")
```
This avoids table locks and long transactions on Postgres.

#### Ordering & dependencies across apps
If a `ForeignKey` points to another app’s model, Django auto-adds a dependency, e.g.:
```python
dependencies = [
    ("catalog", "0010_auto"),
]
```
You can add your own if a data migration must run after another app’s migration.

#### Merge conflicts & branches
When two branches create migrations from the same base, you’ll get a migration conflict. Fix it by creating a merge migration:
```powershell
poetry run python manage.py makemigrations --merge
```
This generates, e.g., 0012_merge_0011_A_0011_B.py that depends on both heads. Inspect and run migrate.

#### Reversibility & testing
* Make data migrations reversible (supply backward) when practical. If not, pass migrations.RunPython.noop as the reverse callable.
* Dry run / inspect:
```powershell
poetry run python manage.py makemigrations --check   # fail CI if migrations needed
poetry run python manage.py showmigrations
poetry run python manage.py migrate --plan           # see planned operations
poetry run python manage.py sqlmigrate products 0005 # preview SQL
```

#### Squashing old migrations
When an app has many migrations, you can squash:
```powershell
poetry run python manage.py squashmigrations products 0001 0050
```
* Produces a single squashed migration. Review carefully, especially data ops.
* Apply squashed migration on new environments; existing DBs with older chain will be recognized as up-to-date.

#### Renames vs drop/create
* Prefer RenameField / RenameModel over removing + adding; you keep data and references.
* If you must split/merge columns, write a schema change + RunPython data migration to move data.

#### When to put logic in migrations vs code
* **Schema definition** (columns, constraints, indexes) → migrations.
* **One-time data changes** to support a schema change → data migration (RunPython).
* **Large/long-running backfills** → custom management command scheduled separately (migrations should be quick and safe to run at deploy time).



---

## 3) Django ORM — quick tour

Interactive shell:
```powershell
python manage.py shell
```
```python
from products.models import Product
p = Product.objects.create(name="Keyboard", price=199.90)
Product.objects.filter(is_active=True).order_by("price")
Product.objects.filter(name__icontains="key")
Product.objects.only("id", "name").values("id", "name")
Product.objects.select_for_update()           # in transactions

from django.db import transaction
with transaction.atomic():
    Product.objects.filter(pk=p.pk).update(price=179.90)
```

Performance tips: use `select_related` (FK), `prefetch_related` (M2M), and avoid N+1 queries in list views.


### Open an interactive shell
```powershell
poetry run python manage.py shell
```
**execute:**
```python
from decimal import Decimal
from django.db import transaction
from django.db.models import Q, F, Count, Sum, Avg, Min, Max, Value, Case, When
from django.db.models.functions import Lower, Coalesce, Concat
from products.models import Product, Category, Tag, ProductTag, ProductStatus
```

#### 1) Create / Read / Update / Delete (CRUD)

**Create**
```python
c = Category.objects.create(name="Keyboards", slug="keyboards")
p = Product.objects.create(name="Keyboard", price=Decimal("199.90"), category=c)
Tag.objects.bulk_create([Tag(name="mechanical", slug="mechanical"),
                         Tag(name="wireless", slug="wireless")])
```

**Read (filtering & ordering)**
```python
Product.objects.filter(is_active=True).order_by("price", "-created_at")
Product.objects.filter(name__icontains="key")                       # LIKE %key%
Product.objects.filter(price__gte=100, price__lt=250)               # range
Product.objects.filter(Q(name__icontains="key") | Q(description__icontains="key"))
Product.objects.exclude(is_active=True)
Product.objects.order_by().values("id", "name")                     # no default ordering
Product.objects.values_list("slug", flat=True)
Product.objects.in_bulk([1, 2, 3])                                  # {id: Product}
Product.objects.first(), Product.objects.last(), Product.objects.get(pk=1)
```

**Update**
```python
# single instance
p.price = Decimal("179.90")
p.save(update_fields=["price", "updated_at"])

# bulk update (no save() signals)
Product.objects.filter(pk=p.pk).update(price=F("price") - 10)

# update_or_create (atomic upsert-style)
obj, created = Product.objects.update_or_create(
    slug="keyboard", defaults={"price": Decimal("189.90")}
)
```

**Delete**
```python
Product.objects.filter(price__lt=Decimal("50")).delete()
```

#### 2) Relations (FK / M2M / reverse)
```python
# FK forward & reverse
p.category            # Category instance or None
c.products.all()      # reverse FK manager

# M2M (explicit through model present)
t = Tag.objects.get(slug="mechanical")
p.tags.add(t)         # works even with through; Django creates ProductTag row
p.tags.all()
t.products.all()

# Through model with extra fields
ProductTag.objects.create(product=p, tag=t, weight=3)
ProductTag.objects.filter(tag__slug="mechanical").select_related("product", "tag")
```

**Performance: join vs prefetch**
```python
# FK / OneToOne: join with select_related
Product.objects.select_related("category").all()

# M2M / Reverse FK: prefetch (two queries, then in-Python join)
Product.objects.prefetch_related("tags")           # all tags
from django.db.models import Prefetch
Product.objects.prefetch_related(
    Prefetch("tags", queryset=Tag.objects.order_by("name"))
)
```

#### 3) Aggregations & annotations
```python
# Aggregations (scalar result)
Product.objects.aggregate(
    avg_price=Avg("price"), max_price=Max("price"), n=Count("id")
)

# Annotate per-row values (adds fields to each instance)
qs = (Product.objects
      .active()
      .annotate(tag_count=Count("tags", distinct=True))
      .annotate(name_ci=Lower("name")))
for row in qs.values("name", "tag_count", "name_ci"):
    print(row)

# Conditional annotation (CASE WHEN)
Product.objects.annotate(
    pricey=Case(When(price__gte=300, then=Value(True)), default=Value(False))
)

# String concatenation
Product.objects.annotate(full=Concat("name", Value(" - "), "slug"))
```
Subqueries / correlated subqueries (advanced)
```python
from django.db.models import OuterRef, Subquery

# Example: tag count via subquery
pt = ProductTag.objects.filter(product=OuterRef("pk")).values("product").annotate(n=Count("*")).values("n")
Product.objects.annotate(tag_n=Coalesce(Subquery(pt), 0)).order_by("-tag_n")
```

##### Aggregations & Annotations
What they are
* **Aggregation**: collapse a queryset to one (or a few) scalar values (e.g., count, average). Returns a dict, not model instances.
* **Annotation**: add computed columns to each row in a queryset (e.g., tag_count, discounted_price) so you can filter/order by them without leaving SQL.

Why use them
* Push computation to the DB (fast, reduces Python loops).
* Avoid N+1: compute counts/sums with COUNT/SUM instead of per-row queries.
* Filter/order by computed values in one round trip.
* Summarize data (dashboards, analytics) or decorate rows (badges, flags).

When to use which
* Use Aggregation when you need a single number/tuple per group: totals, averages, min/max, etc.
* Use Annotation when you still want rows back but with extra fields you can filter/sort on.



#### 4) Transactions & row locking
Atomic blocks
```python
from django.db import transaction

with transaction.atomic():
    p = Product.objects.select_for_update().get(pk=1)  # lock row
    p.price = F("price") + 5
    p.save(update_fields=["price"])
```
select_for_update options (Postgres/MySQL):
```python
# nowait: raise immediately if row is locked; skip_locked: skip locked rows
Product.objects.select_for_update(nowait=True).get(pk=1)
Product.objects.select_for_update(skip_locked=True).filter(status=ProductStatus.PUBLISHED)
```
> Keep transactions short; avoid network calls inside. Use F() expressions for atomic math on the DB side.

##### Transactions & Row Locking
What they are
* **Transaction**: a unit of work that’s all-or-nothing. In Django: transaction.atomic() ensures commit or rollback as one block.
* **Row locking**: prevent concurrent writers from trampling each other by acquiring locks on selected rows (usually via SELECT … FOR UPDATE).

Why use them
* Correctness under concurrency (avoid race conditions like double-spend, negative stock/price).
* Invariants stay true even with many workers/requests.
* Predictable error handling (commit/rollback boundaries).

When to use them
* Read-modify-write sequences that must be consistent (e.g., adjust price/stock).
* Idempotent jobs split across multiple writes.
* “Queue worker” patterns where many workers pull from the same table.



#### 5) Bulk ops & pagination
```python
# Bulk create/update (no signals; partial validation)
ps = [Product(name=f"Prod {i}", price=Decimal("9.99")) for i in range(1000)]
Product.objects.bulk_create(ps, batch_size=500)

# bulk_update (update selected fields on many objects you already loaded)
for p in ps: p.price = Decimal("12.99")
Product.objects.bulk_update(ps, fields=["price"], batch_size=500)

# Pagination (don’t slice deep without ordering)
page = 3; per = 20
qs = Product.objects.order_by("id")[ (page-1)*per : page*per ]
```

Memory-friendly iteration
```python
for p in Product.objects.iterator(chunk_size=2000):
    ...
```

#### 6) Field lookups & transforms (cheat sheet)
* Text: icontains, istartswith, iendswith, regex, iregex, exact, iexact
* Comparisons: lt, lte, gt, gte, range, in, isnull
* Date/time: date, year, month, day, week_day
* Array/JSON (Postgres): contains, contained_by, has_key, has_keys, has_any_keys
* DB functions: Lower, Upper, Length, Trim, Coalesce, Greatest, Least, Now, Extract…
* Distinct: distinct() and Postgres distinct-on: distinct("category") with matching .order_by("category", ...)

#### 7) .values() / .values_list() vs model instances
* values() / values_list() → returns dicts/tuples, faster to serialize, no model methods.
* Model instances → richer but heavier. Use .only() or .defer() to trim columns:
```python
Product.objects.only("id", "name")               # loads only these fields
Product.objects.defer("description", "updated_at")
```

#### 8) Query evaluation & caching
* QuerySets are lazy. They evaluate on iteration or when you call list(), len(), bool(), exists(), etc.
* A QuerySet caches results after first evaluation:
```python
qs = Product.objects.active()
list(qs)        # hits DB
list(qs)        # cached
qs = qs.all()   # same cache; however, changing the queryset (e.g., .filter()) invalidates cache
```
Use exists() when you only care if any row matches:
```python
if Product.objects.filter(slug="x").exists():
    ...
```

#### 9) Debugging queries & profiling
Print SQL of a queryset
```python
print(Product.objects.filter(is_active=True).query)
```

Explain (ask the DB for the plan)
```python
Product.objects.filter(is_active=True).explain()             # backend default
Product.objects.filter(is_active=True).explain(analyze=True) # Postgres: run+plan (careful in prod)
```

Log queries in dev (settings.py)
```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.db.backends": {"handlers": ["console"], "level": "DEBUG"},
    },
}
```
Or use django-debug-toolbar for in-browser query inspection.

#### 10) Common patterns (that save your bacon)
Idempotent create (don’t duplicate rows)
```python
obj, created = Product.objects.get_or_create(
    name="Keyboard",
    defaults={"price": Decimal("199.90")},
)
```

Conditional uniqueness (already modeled), reuse slug after “archive”
```python
# thanks to UniqueConstraint(condition=Q(is_active=True))
Product.objects.create(name="MX Board", is_active=False)
Product.objects.create(name="MX Board", is_active=True)  # allowed
```

Rank/Window functions (Postgres)
```python
from django.db.models import Window
from django.db.models.functions import RowNumber
(Product.objects
 .order_by("category_id", "-created_at")
 .annotate(rownum=Window(expression=RowNumber(), partition_by=["category"], order_by=F("created_at").desc())))
```

Unions / intersections
```python
A = Product.objects.filter(price__lt=100).values("id")
B = Product.objects.filter(is_active=True).values("id")
A.union(B)           # also .intersection(), .difference()
```

#### 11) Transactions patterns & locking options (recap)
* Wrap multi-write operations with @transaction.atomic (in services.py).
* Use select_for_update(of=("self",)) (Postgres) to lock only the selected table if your query joins others.
* nowait=True to fail fast; skip_locked=True for worker-queue style processing.
* Keep atomic blocks small and fast.

#### 12) Pitfalls & fixes
* N+1 queries: fix with select_related() and prefetch_related().
* Counting large tables: qs.count() is SQL COUNT(*) (fast on indexed PK). Don’t len(list(qs)).
* Slicing without order: always order_by before [offset:limit] for deterministic results.
* values() then modifying: dicts don’t have save(). If you need to persist, fetch model instances.
* bulk_* skip signals & auto_now: if you need these, update explicitly or post-process.
* SQLite quirks: schema changes can be slower (temp tables). For prod, use Postgres.

#### 13) A few ready-to-paste recipes
Top tags per product (prefetch to avoid N+1):
```python
from django.db.models import Prefetch
qs = (Product.objects
      .active()
      .prefetch_related(Prefetch("tags", queryset=Tag.objects.order_by("name")))
      .only("id", "name", "slug"))
for p in qs:
    print(p.name, [t.name for t in p.tags.all()[:3]])
```

Atomic stock decrement example:
```python
from django.core.exceptions import ValidationError

@transaction.atomic
def reduce_price(slug: str, amount: Decimal):
    p = Product.objects.select_for_update().get(slug=slug)
    if p.price - amount < 0:
        raise ValidationError("Price cannot go negative")
    p.price = F("price") - amount
    p.save(update_fields=["price", "updated_at"])
```

Search with pagination & total:
```python
q = "board"
base = Product.objects.active().filter(name__icontains=q)
total = base.count()
page, per = 1, 20
rows = (base
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-created_at")
        [(page-1)*per : page*per])
print(total, list(rows))
```


### TL;DR
* Use select_related for FK/O2O; prefetch_related for M2M/reverse.
* Favor F() + atomic blocks for concurrent-safe updates.
* Use annotations (Count/Avg/Case/Subquery) to compute in the DB.
* Keep views thin; put multi-step write logic into services.
* Inspect SQL and EXPLAIN when optimizing; add the right indexes.


---

## 4) Admin Panel

Register the model in `products/admin.py`:
```python
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
```

Create superuser:
```powershell
python manage.py createsuperuser
```
Open `http://127.0.0.1:8000/admin/`.

---

## 5) Views (function & class-based) and URL Routing

**URLs – project level (`config/urls.py`)**
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("products.urls", namespace="products")),
    path("api/", include("products.urls_api")),
]
```

**App URLs – web (`products/urls.py`)**
```python
from django.urls import path
from . import views

app_name = "products"
urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("new/", views.ProductCreateView.as_view(), name="create"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="detail"),
    path("<slug:slug>/edit/", views.ProductUpdateView.as_view(), name="update"),
    path("<slug:slug>/delete/", views.ProductDeleteView.as_view(), name="delete"),
]
```

**Class-based views with generic CRUD (`products/views.py`)**
```python
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product
from .forms import ProductForm

class ProductListView(ListView):
    model = Product
    paginate_by = 10

class ProductDetailView(DetailView):
    model = Product

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("products:list")

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy("products:detail", kwargs={"slug": self.object.slug})

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("products:list")
```

**Forms (`products/forms.py`)**
```python
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "is_active"]
```
---

## 6) Template Language

`templates/base.html`
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{% block title %}Shop{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/app.css' %}">
</head>
<body>
  <header><h1><a href="{% url 'products:list' %}">Shop</a></h1></header>
  <main>{% block content %}{% endblock %}</main>
</body>
</html>
```

`templates/products/product_list.html`
```html
{% extends "base.html" %}
{% block title %}Products{% endblock %}
{% block content %}
  <a href="{% url 'products:create' %}">New Product</a>
  <ul>
    {% for p in object_list %}
      <li><a href="{{ p.get_absolute_url|default:(''|add:p.slug) }}">{{ p.name }}</a> — {{ p.price }}</li>
    {% empty %}
      <li>No products.</li>
    {% endfor %}
  </ul>

  {% if is_paginated %}
    <div>
      {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}">Prev</a>
      {% endif %}
      Page {{ page_obj.number }} of {{ paginator.num_pages }}
      {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}">Next</a>
      {% endif %}
    </div>
  {% endif %}
{% endblock %}
```

`templates/products/product_detail.html`
```html
{% extends "base.html" %}
{% block title %}{{ object.name }}{% endblock %}
{% block content %}
  <h2>{{ object.name }}</h2>
  <p>{{ object.description|linebreaks }}</p>
  <p><b>Price:</b> {{ object.price }}</p>
  <a href="{% url 'products:update' object.slug %}">Edit</a> |
  <a href="{% url 'products:delete' object.slug %}">Delete</a>
{% endblock %}
```

`templates/products/product_form.html`
```html
{% extends "base.html" %}
{% block content %}
  <h2>{{ view.object|yesno:"Edit Product,New Product" }}</h2>
  <form method="post">{% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
  </form>
{% endblock %}
```

`templates/products/product_confirm_delete.html`
```html
{% extends "base.html" %}
{% block content %}
  <h2>Delete {{ object.name }}?</h2>
  <form method="post">{% csrf_token %}
    <button type="submit">Confirm</button>
  </form>
{% endblock %}
```

---

## 7) URL Routing (notes)

- Project `config/urls.py` delegates to app `urls.py`.
- Use `path()` with converters: `<int:id>`, `<slug:slug>`, etc.
- Prefer namespaced URLs to avoid collisions.

---

## 8) Static Files

- Dev: put CSS/JS in `static/` or `app/static/app/...`
- Use `{% load static %}` at top of templates (Django auto-loads in base since we used `{% static %}` already).
- Prod: `python manage.py collectstatic` → `STATIC_ROOT`

---

## 9) Authentication (built-in)

**Enable `django.contrib.auth`, already in INSTALLED_APPS.**  
Add login/logout URLs in `config/urls.py`:
```python
from django.contrib.auth import views as auth_views

urlpatterns += [
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
```

Protect a view:
```python
from django.contrib.auth.mixins import LoginRequiredMixin

class ProductCreateView(LoginRequiredMixin, CreateView):
    ...
```

Template snippets:
```html
{% if user.is_authenticated %}
  Hello, {{ user.username }}! <a href="{% url 'logout' %}">Logout</a>
{% else %}
  <a href="{% url 'login' %}">Login</a>
{% endif %}
```

---

## 10) Signals

`products/signals.py`
```python
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product

@receiver(pre_save, sender=Product)
def product_slug_auto(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)
```

This auto-sets `slug` before save.

---

## 11) Django Commands (manage.py)

Common ones:
```powershell
python manage.py runserver             # dev server
python manage.py makemigrations        # create migration files
python manage.py migrate               # apply migrations
python manage.py createsuperuser
python manage.py shell
python manage.py collectstatic         # for prod
python manage.py test                  # run tests
python manage.py showmigrations
python manage.py sqlmigrate app 0001   # show SQL
```

Custom command example:

`products/management/commands/seed_products.py`
```python
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = "Seed example products"

    def handle(self, *args, **options):
        for name, price in [("Keyboard", 199.90), ("Mouse", 99.90), ("Monitor", 999.00)]:
            Product.objects.get_or_create(name=name, defaults={"price": price})
        self.stdout.write(self.style.SUCCESS("Seeded products"))
```
Run:
```powershell
python manage.py seed_products
```

---

## 12) CRUD (recap)

- We used generic CBVs (CreateView, ListView, DetailView, UpdateView, DeleteView).
- You can also write **function-based views**:

```python
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductForm

def product_list(request):
    qs = Product.objects.filter(is_active=True)
    return render(request, "products/product_list.html", {"object_list": qs})

def product_create(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("products:list")
    return render(request, "products/product_form.html", {"form": form})

def product_detail(request, slug):
    obj = get_object_or_404(Product, slug=slug)
    return render(request, "products/product_detail.html", {"object": obj})
```

---

## 13) Production Database (PostgreSQL)

Install Postgres locally (Windows installer) or use Docker. Example env:
```ini
DEBUG=False
SECRET_KEY=super-secret
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgres://user:pass@localhost:5432/shop
```

Replace DB settings (simple):
```python
import dj_database_url  # optional helper if you install it
DATABASES = {
    "default": dj_database_url.parse(os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"), conn_max_age=600)
}
```
If not using `dj-database-url`, set fields manually:
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PGDATABASE", "shop"),
        "USER": os.getenv("PGUSER", "postgres"),
        "PASSWORD": os.getenv("PGPASSWORD", ""),
        "HOST": os.getenv("PGHOST", "127.0.0.1"),
        "PORT": os.getenv("PGPORT", "5432"),
    }
}
```
Install driver:
```powershell
pip install psycopg2-binary
```

---

#TODO talk about Serializers

## 14) Django REST Framework (DRF)

**Install already done. Add basic API:**

`products/serializers.py`
```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "price", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]
```

`products/api.py`
```python
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # tighten in real apps
```

`products/urls_api.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ProductViewSet

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
```

Test:
- `GET /api/products/`
- `POST /api/products/` with JSON body
- Add auth later: TokenAuth/JWT (e.g., `djangorestframework-simplejwt`)

---

## 15) Authentication for APIs (quick note)

```powershell
pip install djangorestframework-simplejwt
```

In `settings.py`:
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

URLs:
```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns += [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
```

---

## 16) Signals (advanced idea)

- Create a `Profile` automatically on `User` creation, or audit logs on `post_save`.
- Debounce heavy tasks; for truly heavy work, use Celery instead of signals.

---

## 17) Deployment (production checklist + options)

**Security & settings**
- `DEBUG=False`
- Strong `SECRET_KEY` in env
- Set `ALLOWED_HOSTS`
- HTTPS enforced (proxy/Nginx)
- `CSRF_COOKIE_SECURE=True`, `SESSION_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS=...` (after HTTPS works)
- `SECURE_SSL_REDIRECT=True`
- Logging to STDOUT in prod

**Static files**
- Run `python manage.py collectstatic`
- Option A: **WhiteNoise** (simple, app-served)
    ```powershell
    pip install whitenoise
    ```
    In `MIDDLEWARE` (top, after SecurityMiddleware):
    ```python
    "whitenoise.middleware.WhiteNoiseMiddleware",
    ```
    And:
    ```python
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    ```

**Database**
- Use Postgres (as above)
- Apply migrations on deploy

**Process model**
- Linux server (even from Windows dev): Gunicorn + Nginx + systemd
- Alternatively: Docker + a PaaS (Render, Railway, Fly.io, Azure App Service)

**Minimal Docker example** (Linux container; run from WSL/CI):
`Dockerfile`
```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install --no-cache-dir "django>=5,<6" psycopg2-binary python-dotenv djangorestframework whitenoise gunicorn
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "config.wsgi:application", "--bind=0.0.0.0:8000", "--workers=3"]
```

**Nginx (reverse proxy)**
- Proxy to Gunicorn at `localhost:8000`
- Serve `/static/` if not using WhiteNoise

**Basic deploy steps**
1. Set env vars (SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, DATABASE_URL).
2. Install deps.
3. `python manage.py migrate`
4. `python manage.py collectstatic`
5. Start Gunicorn (or ASGI server like Uvicorn if using websockets).
6. Health check endpoint (e.g., `/api/` or custom `/healthz`).

---

## 18) Extra: Testing & CI quickstart

```powershell
python manage.py test
```
Example unit test: `products/tests/test_models.py`
```python
from django.test import TestCase
from products.models import Product

class ProductModelTests(TestCase):
    def test_slug_autoset(self):
        p = Product.objects.create(name="My Name", price=10)
        self.assertTrue(p.slug.startswith("my-name"))
```
Set up GitHub Actions later to run `pip install -r requirements.txt && python manage.py test`.

---

## 19) Common Pitfalls & Pro Tips

- Always commit migrations with model changes.
- Don’t rely on signals for business-critical flows → use services/tasks.
- Use `select_related`/`prefetch_related` in list views.
- Split settings: `settings/base.py`, `settings/dev.py`, `settings/prod.py`.
- Use `.env` for secrets locally; in prod, use real env vars.
- For Windows dev, WSL2 often avoids compilation pain and mirrors Linux prod.

---

If you want, I can package this into a starter repo (with settings split, Docker, WhiteNoise, DRF JWT) or extend with **Celery + Redis**, **HTMX** patterns, or **role-based permissions**.
