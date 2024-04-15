from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (CommonUserViewSet, IngredientViewSet, RecipeViewSet,
                       SubscriptionsList, TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', CommonUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/subscriptions/', SubscriptionsList.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
