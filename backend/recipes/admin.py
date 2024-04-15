
from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import (Favorite, Follow, Ingredient, IngredientRecipe,
                     Recipe, Shoplist, Tag, User)

admin.site.unregister(Group)


class FollowersListFilter(admin.SimpleListFilter):
    title = _('Подписчики и авторы')
    parameter_name = 'followers'

    def lookups(self, request, model_admin):
        return (
            ('followers', _('подписчики')),
            ('followings', _('авторы')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'followers':
            return queryset.filter(follower__user__in=User.objects.all())
        if self.value() == 'followings':
            return queryset.filter(following__user__in=User.objects.all())


@admin.register(User)
class CommonUserAdmin(UserAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name',
                    'is_staff', 'recipes', 'followers', 'followings')
    search_fields = ('username', 'email')
    readonly_fields = ['is_active', 'is_staff', 'is_superuser']
    list_filter = (FollowersListFilter,)

    @display(description='Рецепты')
    def recipes(self, user):
        return user.recipes.count()

    @display(description='Подписчики')
    def followers(self, user):
        return user.following.count()

    @display(description='Подписки')
    def followings(self, user):
        return user.follower.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'following')
    list_filter = ('user', 'following')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'get_color_html', 'slug')
    readonly_fields = ('get_color_html',)

    @display(description='Цвет')
    def get_color_html(self, tag):
        return mark_safe(
            f'<span style="background-color:{tag.color}">'
            '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>'
        )


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class PeriodsCookingtimeListFilter(admin.SimpleListFilter):
    title = _('Время готовки')
    parameter_name = 'period'

    def lookups(self, request, model_admin):
        recipes = Recipe.objects.count()
        if recipes <= 1:
            return None
        cooking_time_recipes = [
            recipe.cooking_time for recipe in Recipe.objects.all()
        ]
        min_cooking_time = min(cooking_time_recipes)
        max_cooking_time = max(cooking_time_recipes)
        if min_cooking_time == max_cooking_time:
            return None
        start, end = 1, 10**10
        periods_count = 3
        one_third = (max_cooking_time - min_cooking_time) // periods_count
        two_third = (max_cooking_time - min_cooking_time) * 2 // periods_count
        return (
            ((start, one_third), _(f'до {one_third} мин')),
            ((one_third, two_third), _(f'от {one_third} до {two_third} мин')),
            ((two_third, end), _(f'от {two_third} мин')),
        )

    def queryset(self, request, recipes):
        period = self.value()
        if period is not None:
            return recipes.filter(cooking_time__range=eval(period))
        return recipes


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)
    list_display = (
        'pk', 'name', 'author', 'cooking_time', 'get_tags', 'get_ingredients',
        'get_recipe_in_favorites', 'get_image'
    )

    list_filter = ('tags', 'author', PeriodsCookingtimeListFilter)
    search_fields = ('name', 'tags__name', 'author__username')
    readonly_fields = ('get_image',)

    @display(description='В избранном')
    def get_recipe_in_favorites(self, recipe):
        return recipe.favorites.count()

    @display(description='Тег')
    def get_tags(self, recipe):
        return mark_safe(
            '<br>'.join(recipe.tags.values_list('name', flat=True))
        )

    @display(description='Продукты')
    def get_ingredients(self, recipe):
        return mark_safe(
            '<br>'.join(
                [f'{ingredient}' for ingredient in recipe.amounts.all()]
            )
        )

    @display(description='Картинка')
    def get_image(self, recipe):
        return mark_safe(
            '<img src="/media/{}" width="40" height="40" />'.format(
                recipe.image
            )
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('measurement_unit',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'ingredient', 'recipe', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    list_filter = ('recipe',)


@admin.register(Shoplist)
class ShoplistAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user')
    list_filter = ('recipe',)
