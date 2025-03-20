from django.urls import path
from . import views  # Ensure you have a view to handle the about page

urlpatterns = [
    path('about/', views.about_view, name='about_view'),
]