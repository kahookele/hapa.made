from django.urls import path
from . import views

urlpatterns = [
    path('', views.market_list, name='market_list'),  # Example route
]