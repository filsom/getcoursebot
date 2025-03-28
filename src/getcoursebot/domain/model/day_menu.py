from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal as D

from getcoursebot.domain.model.proportions import KBJU


class TypeMeal(object):
    BREAKFAST = 1
    LUNCH = 2
    DINNER = 3
    SNACK= 4


@dataclass
class Ingredient:
    name: str
    value: D
    unit: str


@dataclass
class AdjustedRecipe:
    recipe_id: UUID
    name: str
    recipe: str
    photo_id: int
    amount_kkal: D
    type_meal: TypeMeal
    ingredients: list[Ingredient]


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
            adjusted.append(Ingredient(ingredient.name, value, ingredient.unit))
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
        TypeMeal.BREAKFAST: D("30"),
        TypeMeal.LUNCH: D("30"),
        TypeMeal.SNACK: D("15"),
        TypeMeal.DINNER: D("25")
    }
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
            default += recept.amount_kkal
        if user_snack:
            self.my_snack_kkal = user_amount_kkal - D(str(default)).quantize(D("1"))

    def repr(self):
        TYPE_MAP = {
            TypeMeal.BREAKFAST: "завтрак",
            TypeMeal.LUNCH: "обед",
            TypeMeal.DINNER: "ужин",
            TypeMeal.SNACK: "перекус"
        }
        dict_recipes = {}
        for recipe in self.my_recepts:
            str_ingredients = ""
            for ingredient in recipe.ingredients:
                str_ingredients += f"🔹 {ingredient.name.title()} {ingredient.value}{ingredient.unit}\n"
            str_result = f"{TYPE_MAP.get(recipe.type_meal).upper()}: {recipe.name.title()}\n\n{str_ingredients}\n{recipe.recipe}"
            dict_recipes.update({recipe.recipe_id:str_result})
        dict_recipes.update({"amount_kkal": str(self.my_snack_kkal)})
        return dict_recipes