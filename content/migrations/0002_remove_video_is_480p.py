# Generated by Django 5.1.7 on 2025-03-16 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='is_480p',
        ),
    ]
