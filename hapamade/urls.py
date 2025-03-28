"""
URL configuration for hapamade project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from workshop import views as workshop_views  # Import workshop views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('shop/', include('shop.urls')),
    path('workshops/', include('workshop.urls')),
    path('about/', include('about.urls')),
    path('markets/', include('markets.urls')),
    path('booking-success/', workshop_views.booking_success, name='booking_success'),
    path('booking-cancel/', workshop_views.booking_cancel, name='booking_cancel'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)