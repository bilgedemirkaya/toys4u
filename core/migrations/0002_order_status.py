# Generated by Django 5.1.7 on 2025-03-31 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(default='Draft', max_length=20),
        ),
    ]
