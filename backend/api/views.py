from datetime import datetime

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import FilterOfRecipe, IngredientSearchFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CommonUserSerializer, FollowUserSerializer,
                             IngredientSerializer,
                             RecipeCreateUpdateSerializer, RecipeSerializer,
                             RecipeSmallSizeSerializer, TagSerializer)
from api.utils import create_shopping_list
from recipes.models import (Favorite, Follow, Ingredient, Recipe, Shoplist,
                            Tag, User)


class CommonUserViewSet(UserViewSet):
    """Вьюсет модели Users."""
    queryset = User.objects.all()
    serializer_class = CommonUserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action in ('me',):
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        user = self.request.user
        following = get_object_or_404(User, id=id)

        if self.request.method == 'POST':
            if user == following:
                raise exceptions.ValidationError({
                    'Невозможно подписаться на самого себя.'
                })
            subscription, created = Follow.objects.get_or_create(
                user=user, following=following
            )
            if not created:
                raise exceptions.ValidationError({
                    (f'Вы уже подписаны на автора: {following.first_name}'
                     f' {following.last_name}.')
                })
            return Response(
                FollowUserSerializer(
                    following,
                    context={'request': request}
                ).data,
                status.HTTP_201_CREATED
            )
        following.delete()
        return Response(
            (f'Вы отписались от автора: {following.first_name}'
             f' {following.last_name}.'),
            status.HTTP_204_NO_CONTENT)


class SubscriptionsList(generics.ListCreateAPIView):
    """Подписки пользователя."""
    serializer_class = FollowUserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class RetrieveListViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class TagViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterOfRecipe
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def add_or_delete_recipe(self, request, model, pk):
        """Вспомогательная функция для методов 'favorite', 'shoping_cart'."""
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if self.request.method == 'POST':
            in_collection, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if not created:
                raise exceptions.ValidationError({
                    f'Рецепт {recipe.name} уже добавлен.'
                })
            return Response(
                RecipeSmallSizeSerializer(recipe).data,
                status.HTTP_201_CREATED
            )
        get_object_or_404(model, recipe_id=pk).delete()
        return Response('Рецепт удалён.', status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавление или удаление рецепта из избранного."""
        return self.add_or_delete_recipe(request, Favorite, pk)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление или удаление рецепта из списка покупок."""
        return self.add_or_delete_recipe(request, Shoplist, pk)

    @action(detail=False,
            methods=('get',),
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        """Выгружает общий список продуктов из рецептов,
        добавленных в список покупок."""
        user = request.user
        return FileResponse(
            create_shopping_list(
                Shoplist.recipes_in_shoplist(user),
                Shoplist.ingredients_in_shoplist(user)
            ),
            as_attachment=True,
            filename=f'Список покупок {datetime.today():%d.%m.%Y}.txt'
        )
