from django.urls import path
from .views import workshop_list, book_workshop, booking_success

urlpatterns = [
    path('', workshop_list, name='workshop_list'),  # ✅ This handles /workshops/
    path('book/<int:workshop_id>/', book_workshop, name='book_workshop'),  # ✅ This handles /workshops/book/ID/
    path('booking-success/', booking_success, name='booking_success'),  # Add this
]