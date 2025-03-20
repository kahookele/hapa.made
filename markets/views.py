from django.shortcuts import render
from .models import Market

# Create your views here.

def market_list(request):
    # Fetch all market entries from the database
    markets = Market.objects.all()
    
    # Pass the markets to the template
    return render(request, "markets/markets.html", {'markets': markets})