from aiogram import Router
from .dialog_with_training import training_dialog
from .dialog_with_new_training import new_training_dialog
from .dialog_with_food import (
    calculate_kbju_dialog,
    with_data_dialog, 
    food_dialog, 
    input_kbju_dialog,
)
from .dialog_with_day_menu import day_menu_dialog


content_router = Router()
content_router.include_router(training_dialog)
content_router.include_router(new_training_dialog)
content_router.include_router(day_menu_dialog)
content_router.include_router(calculate_kbju_dialog)
content_router.include_router(with_data_dialog)
content_router.include_router(food_dialog)
content_router.include_router(input_kbju_dialog)
