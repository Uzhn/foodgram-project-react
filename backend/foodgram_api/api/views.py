from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilters
from api.permissions import IsAuthorAdminOrReadOnly
from api.serializers import (IngredientSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipeMinifiedSerializer, RecipeSerializer,
                             ShoppingCartSerializer, SubscriptionSerializer,
                             TagSerializer)
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import CustomUser, Subscription


class CustomUserViewSet(UserViewSet):
    """Вьюсет модели пользователя, наследуется от djoser.views.UserViewSet."""
    # queryset = CustomUser.objects.all()

    @action(detail=False, permission_classes=(IsAuthenticated, ))
    def subscriptions(self, request):
        """Метод возвращает список подписок пользователя."""
        queryset = CustomUser.objects.filter(following__user=request.user)
        subs = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            subs, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated, ))
    def subscribe(self, request, **kwargs):
        """Метод подписки/отписки на пользователя."""
        subscription = get_object_or_404(CustomUser, id=kwargs['id'])
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                subscription, data=request.data,
                context={
                    'request': request,
                    'subscription': subscription
                })
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(
                user=request.user, subscription=subscription)
            return Response(serializer.data)
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription, user=request.user,
                subscription=subscription)
            subscription.delete()
            return Response('Вы отписались от автора')


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет модели ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели рецепта."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    @action(detail=False, permission_classes=(IsAuthenticated, ))
    def download_shopping_cart(self, request):
        """Метод возвращает список покупок."""
        ing_in_rep = IngredientInRecipe.objects.filter(
            name__recipe_in_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ing_amount=Sum('amount'))
        shopping_lst = ['Список покупок:\n']
        for ing in ing_in_rep:
            name = ing['ingredient__name'].capitalize()
            unit = ing['ingredient__measurement_unit']
            amount = ing['ing_amount']
            shopping_lst.append(f'\n{name} ({unit}) — {amount}')
        response = HttpResponse(shopping_lst,
                                content_type='text/plain; charset=utf-8')
        filename = f'{request.user.username}_shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthorAdminOrReadOnly, ))
    def shopping_cart(self, request, **kwargs):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        products = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(products, data=request.data,
                                                context={'request': request,
                                                         'products': products,
                                                         })
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=request.user, recipe=products)
            return Response(serializer.data)
        if request.method == 'DELETE':
            favorites = get_object_or_404(
                ShoppingCart, user=request.user, recipe=products)
            favorites.delete()
            return Response('Вы удалили рецепт из списка покупок')

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        favorites = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeMinifiedSerializer(
                favorites, data=request.data,
                context={'request': request,
                         'favorites': favorites
                         })
            serializer.is_valid(raise_exception=True)
            Favorites.objects.create(user=request.user, recipe=favorites)
            return Response(serializer.data)
        if request.method == 'DELETE':
            favorites = get_object_or_404(
                Favorites, user=request.user, recipe=favorites)
            favorites.delete()
            return Response('Вы удалили рецепт из избранного')
