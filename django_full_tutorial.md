
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



**Project layout (goal)**
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

**.env (local development)**
```ini
DEBUG=True
SECRET_KEY=dev-secret-CHANGE_ME
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

**Load env & base settings (edit `config/settings.py`)**
```python
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "insecure")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    # local
    "products",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# DB (sqlite for dev; see production section for Postgres)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3"
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # for collectstatic in prod
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

Run initial migration and dev server:
```powershell
python manage.py migrate
python manage.py runserver
```

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
