# Generated by Django 5.0.6 on 2024-05-26 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0013_consumidor_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumidor',
            name='username',
            field=models.CharField(blank=True, max_length=100, verbose_name='Username'),
        ),
    ]
