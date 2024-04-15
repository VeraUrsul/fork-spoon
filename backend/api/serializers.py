from collections import Counter

import webcolors
from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers

from recipes.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                            Recipe, Shoplist, Tag, User)


class CommonUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, following):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, following=following
        ).exists()


class LittleRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации по рецепту."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(CommonUserSerializer):
    """Сериализатор для отображения информации об авторе,
    на которого подписался пользователь."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta(CommonUserSerializer.Meta):
        fields = (
            *CommonUserSerializer.Meta.fields, 'recipes_count', 'recipes'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        try:
            limit = int(request.GET.get('recipes_limit', 10**10))
        except Exception:
            raise exceptions.ValidationError({
                'Введите число!'
            })
        recipes = obj.recipes.all()[:limit]
        return LittleRecipeSerializer(recipes, many=True).data


class Hex2NameColorTagField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return webcolors.hex_to_name(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""
    color = Hex2NameColorTagField()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateUpdateRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для внесения ингредиентов в рецепт."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='Мера продукта должна быть 1 или более.'
            ),
        )
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецепта."""
    author = CommonUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='amounts'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def recipe_in_collection(self, model, recipe):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return model.objects.filter(user=user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        return self.recipe_in_collection(Favorite, recipe)

    def get_is_in_shopping_cart(self, recipe):
        return self.recipe_in_collection(Shoplist, recipe)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и изменения рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = CreateUpdateRecipeIngredientsSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                1,
                message='Время приготовления должно быть не менее 1 минуты.'
            ),
        )
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )

    @staticmethod
    def unique_object(collection):
        """Вспомогательная функция для методов:
        'validate_tags', 'validate_ingredients'.
        Проверяет уникальность объектов."""
        counter = Counter(collection)
        repeated_elements = [
            item for item, count in counter.items() if count > 1
        ]
        if repeated_elements:
            raise exceptions.ValidationError({
                f'"{repeated_elements}" указан(ы) повторно!'
            })
        return collection

    @staticmethod
    def not_empty_object(collection):
        """Вспомогательная функция для методов:
        'validate_tags', 'validate_ingredients'.
        Проверяет отсутствие пустых полей."""
        if not collection:
            raise exceptions.ValidationError(
                'Это поле обязательное для заполнения!'
            )

    def validate_tags(self, tags):
        """Проверяет валидность данных поля 'tags'."""
        self.not_empty_object(tags)
        self.unique_object(tags)
        return tags

    def validate_ingredients(self, ingredients):
        """Проверяет валидность данных поля 'ingredients'."""
        self.not_empty_object(ingredients)
        ingredients_id = [ingredient['id'] for ingredient in ingredients]
        self.unique_object(ingredients_id)
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        """Вспомогательная функция для методов 'create' и 'update'."""
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient['id'].id,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        instance.tags.set(tags)
        ingredients = validated_data.pop('ingredients', None)
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context=self.context
        ).data


class RecipeSmallSizeSerializer(serializers.ModelSerializer):
    """Сериализатор краткой информации по рецепту."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
