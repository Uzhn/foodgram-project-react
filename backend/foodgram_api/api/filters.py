from django_filters import rest_framework
from recipes.models import Ingredient, Recipe, Tag


class RecipeAnonymousFilters(rest_framework.FilterSet):
    """Фильтрация по тегу для анонимных пользователей."""

    tags = rest_framework.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ('tags',)


class RecipeFilters(RecipeAnonymousFilters):
    """Фильтрация рецептов для авторизованных пользователей."""

    is_favorited = rest_framework.BooleanFilter(
        method='filter_favorited'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_shopping_cart'
    )
    author = rest_framework.NumberFilter(field_name='author__id')

    class Meta:
        model = RecipeAnonymousFilters.Meta.model
        fields = RecipeAnonymousFilters.Meta.fields + ('author',)

    def filter_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_in_favorites__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(recipe_in_cart__user=self.request.user)
        return queryset


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
