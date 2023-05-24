from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated


from api.serializers import (UserSerializer, RecipeSerializer, TagSerializer, IngredientSerializer,
                             SubscriptionSerializer)
from recipes.models import Recipe, Tag, Ingredient, IngredientInRecipe
from users.models import CustomUser, Subscription


class CustomUserViewSet(UserViewSet):
    """Вьюсет модели пользователя, наследуется от djoser.views.UserViewSet."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (AllowAny, )

    @action(detail=False)
    def subscriptions(self, request):
        """Метод возвращает список подписок пользователя."""
        subs = CustomUser.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(subs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, **kwargs):
        """Метод подписки/отписки на пользователя."""
        subscription = get_object_or_404(CustomUser, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = SubscriptionSerializer(subscription, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=request.user, subscription=subscription)
            return Response(serializer.data)
        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscription, user=request.user, subscription=subscription)
            subscription.delete()
            return Response('Вы отписались от автора')


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет модели ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """Метод создает рецепт, где автором является текущий пользователь."""
        serializer.save(author=self.request.user)

    @action(detail=False, permission_classes=(IsAuthenticated, ))
    def download_shopping_cart(self, request):
        """Метод возвращает список покупок."""
        ing_in_rep = IngredientInRecipe.objects.filter(name__recipe_in_cart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ing_amount=Sum('amount'))
        print(ing_in_rep)
        shopping_lst = ['Список покупок:\n']
        for ing in ing_in_rep:
            name = ing['ingredient__name'].capitalize()
            unit = ing['ingredient__measurement_unit']
            amount = ing['ing_amount']
            shopping_lst.append(f'\n{name} ({unit}) — {amount}')
        response = HttpResponse(shopping_lst, content_type='text/plain; charset=utf-8')
        filename = f'{request.user.username}_shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


