from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

class Workshop(models.Model):
    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Advanced Beginner', 'Advanced Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seats_available = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Beginner')

    def __str__(self):
        return f"{self.title} - {self.difficulty}"

class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)  # Store Stripe session ID

    def __str__(self):
        return f"{self.name} - {self.workshop.title} - {self.payment_status}"

@receiver(post_delete, sender=Booking)
def increment_seats_when_booking_deleted(sender, instance, **kwargs):
    instance.workshop.seats_available += 1
    instance.workshop.save()