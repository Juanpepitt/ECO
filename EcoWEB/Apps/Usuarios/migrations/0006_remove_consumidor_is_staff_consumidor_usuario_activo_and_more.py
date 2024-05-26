# Generated by Django 5.0.6 on 2024-05-26 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0005_alter_consumidor_options_alter_consumidor_managers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumidor',
            name='is_staff',
        ),
        migrations.AddField(
            model_name='consumidor',
            name='usuario_activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='consumidor',
            name='usuario_administrador',
            field=models.BooleanField(default=False),
        ),
    ]
