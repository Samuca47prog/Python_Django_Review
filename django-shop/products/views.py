from django.shortcuts import render

# Create your views here.

def about_products(request):
    products = []
    return render(request, "products/about.html", {"products": products})
