from datetime import datetime


def create_shopping_list(recipes, shopping_list):
    recipes_list = '\n'.join(
        f'{index}. {item}' for index, item in enumerate(
            [recipe['recipe__name'] for recipe in recipes],
            start=1
        )
    )
    products = '\n'.join([
        f'* {ingredient["recipe__ingredients__name"]} '
        f'- {ingredient["amount"]} '
        f'({ingredient["recipe__ingredients__measurement_unit"]})'
        for ingredient in shopping_list
    ])
    return (
        'Список продуктов для приготовления рецептов из Fork-Spoon\n'
        f'Дата создания списка {datetime.today():%d.%m.%Y} г.\n'
        'Рецепты:\n'
        f'{recipes_list}'
        '\n'
        'Продукты:\n'
        f'{products}'
    )
