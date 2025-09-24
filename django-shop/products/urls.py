from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "products"

urlpatterns = [
    path("about/", views.about_products, name="about"),
]
