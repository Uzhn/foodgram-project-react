# Generated by Django 4.2.1 on 2023-05-23 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_ingredient_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='measurement_unit',
            field=models.CharField(max_length=200, verbose_name='Единицы измерения'),
        ),
    ]
