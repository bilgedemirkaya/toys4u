# Generated by Django 5.1.7 on 2025-04-03 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_toyreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='toy',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
