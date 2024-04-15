from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Sum

INFO_ABOUT_INGREDIENT = '{ingredient} - {amount} {measurement_unit}'
INFO_ABOUT_RECIPE = 'Рецепт: {name:.15}, Автор: {author}'
RECIPE_IN_FAVORITES = 'Рецепт "{recipe:15}" в избранном у пользователя: {user}'
SHOPLIST = 'Список покупок: {recipe:30} пользователя: {user}'
SUBSCRIPTION = 'Пользователь {user} подписался на {author}'


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='E-mail адрес',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин',
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='Пара подписчик-автор уникальна'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='Невозможность подписки на себя'
            ),
        ]

    def __str__(self):
        return SUBSCRIPTION.format(
            user=self.user.username,
            author=self.following.username,
        )


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        verbose_name='HEX-код',
        validators=[
            RegexValidator(
                regex='^#[A-Fa-f0-9]{6}$',
                message='Вы ввели некорректное значение цвета в формате HEX!'
            )
        ]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Мера',
        max_length=200
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        upload_to=settings.IMAGE_PLACEMENT,
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return INFO_ABOUT_RECIPE.format(
            name=self.name,
            author=self.author.username
        )


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Продукт'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Мера'
    )

    class Meta:
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return INFO_ABOUT_INGREDIENT.format(
            ingredient=self.ingredient.name,
            amount=self.amount,
            measurement_unit=self.ingredient.measurement_unit
        )


class BaseUserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'


class Favorite(BaseUserRecipe):

    class Meta(BaseUserRecipe.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite_recipes')
        ]

    def __str__(self):
        return RECIPE_IN_FAVORITES.format(
            recipe=self.recipe.name,
            user=self.user.username
        )


class Shoplist(BaseUserRecipe):

    class Meta(BaseUserRecipe.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_list_of_recipe')
        ]

    def __str__(self):
        return SHOPLIST.format(
            recipe=self.recipe.name,
            user=self.user.username
        )

    @classmethod
    def recipes_in_shoplist(cls, user):
        recipes = user.shoplists.values('recipe__name')
        return recipes

    @classmethod
    def ingredients_in_shoplist(cls, user):
        return user.shoplists.values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit',
        ).annotate(
            amount=Sum(
                'recipe__amounts__amount'
            )
        )
