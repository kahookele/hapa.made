# Generated by Django 5.1.7 on 2025-03-22 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workshop', '0011_booking_payment_status_booking_stripe_session_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='workshop',
            name='location',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
