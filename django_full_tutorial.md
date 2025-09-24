
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

`products/apps.py` comes pre-generated. Enable signals in `products/__init__.py`:
```python
default_app_config = "products.apps.ProductsConfig"
```

And in `products/apps.py`:
```python
from django.apps import App, apps

class ProductsConfig(App):
    name = "products"

    def ready(self):
        from . import signals  # noqa: F401
```

---

## 2) Models

`products/models.py`
```python
from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    name = models.CharField(maxlength=120, unique=True)
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
> **Note:** If `maxlength` raises an error, use `max_length` (the correct Django argument).

```powershell
python manage.py makemigrations
python manage.py migrate
```

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
