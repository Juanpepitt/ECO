# Generated by Django 5.0.6 on 2024-06-19 16:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ultimo_mensaje', models.TextField(blank=True, null=True)),
                ('fecha_ultimo_mensaje', models.DateTimeField(blank=True, null=True)),
                ('participante1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversaciones_participante1', to=settings.AUTH_USER_MODEL)),
                ('participante2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversaciones_participante2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha_envio', models.DateTimeField(auto_now_add=True)),
                ('conversacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes', to='Mensajes.conversacion')),
                ('emisor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensajes_enviados', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
