from django.urls import path
from .views import workshop_list, book_workshop, booking_success, booking_cancel

urlpatterns = [
    path('', workshop_list, name='workshop_list'),  # ✅ This handles /workshops/
    path('book/<int:workshop_id>/', book_workshop, name='book_workshop'),  # ✅ This handles /workshops/book/ID/
    path('booking-success/', booking_success, name='booking_success'),  # Add this
    path('booking-cancel/', booking_cancel, name='booking_cancel'),
]
