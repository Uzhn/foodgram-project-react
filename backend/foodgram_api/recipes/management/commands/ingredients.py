import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'data/ingredients.json')
        with open(path, encoding='utf-8') as file:
            data = json.load(file)
            for ingredient in data:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Successfully entered the data into the database'))
