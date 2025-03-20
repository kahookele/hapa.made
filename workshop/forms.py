from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone']

    def clean_email(self):
        email = self.cleaned_data['email']
        if Booking.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already used for a booking.")
        return email
