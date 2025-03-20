from django.db import models

# Create models here
class AboutMe(models.Model):
    image = models.ImageField(upload_to='about_images/', blank=True, null=True)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    background_description = models.TextField(blank=True, null=True)  # Optional field
    mission_and_values = models.TextField()  # Mandatory field
    personal_touch = models.TextField(blank=True, null=True)  # Optional field

    def __str__(self):
        return self.name
