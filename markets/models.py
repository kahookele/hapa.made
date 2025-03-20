from django.db import models

class Market(models.Model):
    name = models.CharField(max_length=50)  # Short market name
    location = models.CharField(max_length=255)  # Address
    description = models.TextField(blank=True, null=True)  # Optional field
    date = models.DateField()  # Date of open market
    open_time = models.TimeField()  # Opening time
    close_time = models.TimeField()  # Closing time

    def google_maps_link(self):
        return f"https://www.google.com/maps/search/?api=1&query={self.location.replace(' ', '+')}"

    def apple_maps_link(self):
        return f"https://maps.apple.com/?q={self.location.replace(' ', '+')}"

    def __str__(self):
        return self.name
