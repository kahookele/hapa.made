from django.urls import path
from .views import workshop_list, book_workshop, booking_success

urlpatterns = [
    path('', workshop_list, name='workshop_list'),  # ✅ This handles /workshops/
    path('book/<int:workshop_id>/', book_workshop, name='book_workshop'),  # ✅ This handles /workshops/book/ID/
    path('booking-success/', booking_success, name='booking_success'),  # Add this
]

# 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