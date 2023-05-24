import base64

from django.core.files.base import ContentFile

from djoser.serializers import PasswordSerializer
from rest_framework import serializers, validators

from users.models import CustomUser, Subscription
from recipes.models import (Recipe, Tag, Ingredient, IngredientInRecipe,
                            ShoppingCart, Favorites)


class Base64ImageField(serializers.ImageField):
    """Кастомный тип поля для декодирования изображения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.follower.filter(subscription=obj).exists()


class AuthUserSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class SetPasswordSerializer(PasswordSerializer):
    """Сериализатор для изменения пароля пользователя."""

    current_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели тега."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели ингредиента в рецепте."""

    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта."""
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(read_only=True, many=True, source='recipes')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        """Метод проверяет наличие рецепта в избранном."""
        user = self.context['request'].user.is_authenticated
        return Favorites.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод проверяет наличие рецепта в корзине."""
        user = self.context['request'].user.is_authenticated
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор уменьшенного рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор модели подписки."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeMinifiedSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count')
    #     validators = [
    #         validators.UniqueTogetherValidator(
    #             queryset=Follow.objects.all(),
    #             fields=('user', 'following'),
    #             message='Вы уже подписаны на данного пользователя.',
    #         )
    #     ]
    #
    # def validate(self, data):
    #     if self.context['request'].user == data['following']:
    #         raise serializers.ValidationError(
    #             'Вы не можете подписаться на самого себя.'
    #         )
    #     return data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.follower.filter(subscription=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
