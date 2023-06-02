from django.shortcuts import get_object_or_404

from recipes.models import IngredientInRecipe, Ingredient


def create_update_ing(ingredients, recipe):
    """Вспомогательная функция для добавления ингредиентов.
    Используется при создании/редактировании рецепта."""
    ing_lst = []
    for ingredient in ingredients:
        ing_lst.append(
            IngredientInRecipe(
                name=recipe,
                ingredient=ingredient['ingredient'].get('id'),
                amount=ingredient.get('amount')
            )
        )
    IngredientInRecipe.objects.bulk_create(ing_lst)


