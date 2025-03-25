from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum, auto
from typing import Literal
from uuid import UUID
from decimal import Decimal as D

from getcoursebot.domain.model.proportions import KBJU


UNIT = Literal["мл", "шт", "г"]


class TypeMeal:
    Breakfast = 1
    Lunch = 2
    Dinner = 3
    Snack= 4


@dataclass
class Ingredient:
    name: str
    value: D
    unit: UNIT


@dataclass
class AdjustedIngredient:
    name: str
    value: D
    unit: UNIT


@dataclass
class AdjustedRecipe:
    recipe_id: int
    name: str
    recipe: str
    photo_id: int
    amount_kkal: D
    type_meal: TypeMeal
    ingredients: list[AdjustedIngredient]


@dataclass
class Recipe:
    recipe_id: int
    name: str
    recipe: str
    photo_id: str
    amount_kkal: D
    kbju: KBJU
    type_meal: TypeMeal
    ingredients: list[Ingredient]

    def adjust(self, meal_kkal: D) -> AdjustedRecipe:        
        scale = meal_kkal / self.amount_kkal
        adjusted = []
        for ingredient in self.ingredients:
            adjusted_amount = round(ingredient.value * scale)
            adjusted_amount = str(adjusted_amount)
            value = D(adjusted_amount).quantize(D("1"))
            if value == 0:
                value = D("1")
            adjusted.append(AdjustedIngredient(ingredient.name, value, ingredient.unit))
        return AdjustedRecipe(
            self.recipe_id, 
            self.name,
            self.recipe,
            self.photo_id,
            meal_kkal, 
            self.type_meal,
            adjusted
        )


@dataclass
class DayMenu:
    ratio = {
        TypeMeal.Breakfast: D("30"),
        TypeMeal.Lunch: D("30"),
        TypeMeal.Snack: D("15"),
        TypeMeal.Dinner: D("25")
    }
    
    user_id: int
    created_at: datetime
    my_snack_kkal: D | None = None
    my_recepts: list[AdjustedRecipe] | None = field(default_factory=list)

    def set_positions(
        self, 
        recepts: list[Recipe], 
        user_amount_kkal: D, 
        user_snack: bool = False
    ) -> None:
        for recept in recepts:
            amount_meal_kkal_1 = user_amount_kkal*(1 - self.ratio[recept.type_meal]/100)
            cor = user_amount_kkal - amount_meal_kkal_1
            self.my_recepts.append(recept.adjust(cor.quantize(D("1"))))
        
        default = D("0")
        for recept in self.my_recepts:
            print(recept.amount_kkal)
            default += recept.amount_kkal
        if user_snack:
            self.my_snack_kkal = D(str(default)).quantize(D("1"))

    def repr(self):
        TYPE_MAP = {
            TypeMeal.Breakfast:"завтрак",
            TypeMeal.Lunch:"обед",
            TypeMeal.Dinner:"ужин",
            TypeMeal.Snack:"перекус"
        }
        list_recipes = []
        for recipe in self.my_recepts:
            str_ingredients = ""
            for ingredient in recipe.ingredients:
                str_ingredients += f"🔹 {ingredient.name.title()} {ingredient.value}{ingredient.unit}\n"
            repr_recipe = {
                "title": f"{TYPE_MAP.get(recipe.type_meal).upper()}: {recipe.name.title()}\n",
                "ingredients": str_ingredients,
                "text": f"{recipe.recipe}\n",
                "photo_id": recipe.photo_id
            }
            list_recipes.append(repr_recipe)
        return list_recipes
