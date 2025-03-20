# Generated by Django 5.1.7 on 2025-03-17 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutMe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('background_description', models.TextField(blank=True, null=True)),
                ('mission_and_values', models.TextField()),
                ('personal_touch', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
