from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import CustomUser


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField('Название', max_length=200)
    color = models.CharField('Цвет формата HEX', max_length=7,
                             validators=[
                                 RegexValidator(
                                     '^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                                     message='Неверное значение формата HEX'
                                 )])
    slug = models.SlugField('Слаг', max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единицы измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='recipes'
    )
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientInRecipe',
                                         verbose_name='Ингредиенты'
                                         )
    tags = models.ManyToManyField(Tag,
                                  verbose_name='Теги',
                                  related_name='recipes')
    cooking_time = models.IntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(1, message='>= 1')],
        default=1
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингредиентов в рецепте."""
    name = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                             related_name='recipes', verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   related_name='ingredients_in_recipe',
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField('Количество',
                                         validators=[
                                             MinValueValidator(
                                                 1, message='>= 1')])

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient} в {self.name}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='user_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_in_cart',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'


class Favorites(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='user_favorites',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='recipe_in_favorites',
                               verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='user_recipe'
                                    )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'
