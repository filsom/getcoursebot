from dataclasses import dataclass
from decimal import Decimal as D
from uuid import UUID

from getcoursebot.domain.model.day_menu import Ingredient, Recipe, TypeMeal
from getcoursebot.domain.model.proportions import KBJU, TargetProcent, СoefficientActivity

@dataclass
class CreateUserCommand:
    user_id: int
    email: int


@dataclass
class AddRecipeCommand:
    name: str
    recipe: str
    photo_id: int
    amount_kkal: D
    kbju: KBJU
    type_meal: TypeMeal
    ingredients: list[Ingredient]


@dataclass
class MakeDayMenuCommand:
    user_id: int
    recipes: list[Recipe]
    my_snack: bool


@dataclass
class CalculateDayNormCommand:
    user_id: int
    age: int
    height: int
    weight: int 
    coefficient: СoefficientActivity
    target_procent: TargetProcent


@dataclass
class InputeDayNormCommand:
    user_id: int
    kkal: int
    b: int
    j: int 
    u: int
    coefficient: СoefficientActivity
    target_procent: TargetProcent


@dataclass
class AddTrainingCommand:
    user_id: int
    category_id: int
    text: int
    videos_id: list[int]