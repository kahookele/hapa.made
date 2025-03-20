from django.urls import path
from .views import shop_view

urlpatterns = [
    path('', shop_view, name='shop_view'),
]