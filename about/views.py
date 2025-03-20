from django.shortcuts import render
from .models import AboutMe

# Create your views here.

def about_view(request):
    # Fetch the first AboutMe instance from the database
    about = AboutMe.objects.first()
    
    # Pass the about instance to the template
    return render(request, 'about/about.html', {'about': about})