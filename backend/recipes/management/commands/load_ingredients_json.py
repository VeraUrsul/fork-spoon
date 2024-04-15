import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Ингредиенты загружаются ... ')
        try:
            with open(
                './data/ingredients.json', 'r', encoding='utf-8'
            ) as ingredients_file:
                data = json.load(ingredients_file)
            Ingredient.objects.bulk_create(
                Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                ) for row in data
            )
            print('Загрузка ингредиентов завершилась успешно!')
        except FileNotFoundError:
            raise CommandError('Файл с ингредиентами не найден')
