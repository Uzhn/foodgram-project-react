import base64

from django.core.files.base import ContentFile

from rest_framework import serializers

from api.utils import create_update_ing
from recipes.models import (Favorites, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import CustomUser, Subscription


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
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return user.follower.filter(subscription=obj).exists()


class AuthUserSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')

    def create(self, validated_data):
        """Метод создает пользователя и хэширует пароль."""
        user = CustomUser.objects.create(**validated_data)
        user.set_password(user.password)
        user.save()
        return user


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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели рецепта."""
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        read_only=True, many=True, source='recipes')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        """Метод проверяет наличие рецепта в избранном."""
        user = self.context['request'].user
        if not user.is_anonymous:
            return Favorites.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод проверяет наличие рецепта в корзине."""
        user = self.context['request'].user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    ingredients = IngredientInRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        """Метод создания рецепта."""
        request = self.context['request']
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        create_update_ing(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецепта."""
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.ingredients.clear()
        create_update_ing(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        """Метод сериализации данных."""
        request = self.context.get('request')
        return RecipeSerializer(instance, context={'request': request}).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор уменьшенного рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['request'].user
        favorites = self.context['favorites']
        if Favorites.objects.filter(user=user, recipe=favorites).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном.'
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор модели подписки."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeMinifiedSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count')
        read_only_fields = ('email', 'username', 'first_name', 'last_name',
                            'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        user = self.context['request'].user
        subscription = self.context['subscription']
        if user == subscription:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.'
            )
        if Subscription.objects.filter(user=user,
                                       subscription=subscription).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя.'
            )
        return data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.follower.filter(subscription=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор модели корзины покупок."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = self.context['request'].user
        products = self.context['products']
        if ShoppingCart.objects.filter(user=user, recipe=products).exists():
            raise serializers.ValidationError(
                'Этот рецепт уже есть в списке покупок.'
            )
        return data
