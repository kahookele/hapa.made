from django.shortcuts import render
from .models import Product

# Create your views here.
def shop_view(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/shop.html', context)