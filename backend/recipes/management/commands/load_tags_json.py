import json

from django.core.management import BaseCommand, CommandError

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Теги загружаются ... ')
        try:
            with open('./data/tags.json', 'r', encoding='utf-8') as tags_file:
                data = json.load(tags_file)
            Tag.objects.bulk_create(
                Tag(
                    name=row['name'],
                    color=row['color'],
                    slug=row['slug']
                ) for row in data
            )
            print('Загрузка тегов завершилась успешно!')
        except FileNotFoundError:
            raise CommandError('Файл с тегами не найден')
