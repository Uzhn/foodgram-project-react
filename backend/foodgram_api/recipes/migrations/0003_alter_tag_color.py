# Generated by Django 4.2.1 on 2023-05-28 12:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_favorites_user_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, validators=[django.core.validators.RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', message='Неверное значение формата HEX')], verbose_name='Цвет формата HEX'),
        ),
    ]
