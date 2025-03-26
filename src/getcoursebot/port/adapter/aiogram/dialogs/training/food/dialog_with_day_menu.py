from datetime import datetime
import operator
from aiogram.enums import ContentType
from aiogram import Bot, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from getcoursebot.application.commands import MakeDayMenuCommand
from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.domain.model.day_menu import Recipe, TypeMeal
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_states import PaidStartingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import DayMenuDialog, FoodDialog


class Getter:
    @staticmethod
    @inject
    async def get_breakfast(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService], 
        **kwargs
    ):
        result = await service.query_for_menu(TypeMeal.Breakfast)
        dialog_manager.start_data["temporal_recipes"].append(result["class"])
        image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(result["photo_id"]))
        return {
            "photo": image,
            "ingredients": "".join(result["ingredients"]),
            "name": result["name"]
        }
    
    @staticmethod
    @inject
    async def get_lunch(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService], 
        **kwargs
    ):
        result = await service.query_for_menu(TypeMeal.Lunch)
        dialog_manager.start_data["temporal_recipes"].append(result["class"])
        image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(result["photo_id"]))
        print(result["ingredients"])
        return {
            "photo": image,
            "ingredients": "".join(result["ingredients"]),
            "name": result["name"]
        }
    
    @staticmethod
    @inject
    async def get_dinner(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService], 
        **kwargs
    ):
        result = await service.query_for_menu(TypeMeal.Dinner)
        dialog_manager.start_data["temporal_recipes"].append(result["class"])
        image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(result["photo_id"]))
        return {
            "photo": image,
            "ingredients": "".join(result["ingredients"]),
            "name": result["name"]
        }
        
    @staticmethod
    @inject
    async def get_snack(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService], 
        **kwargs
    ):
        result = await service.query_for_menu(TypeMeal.Snack)
        dialog_manager.start_data["temporal_recipes"].append(result["class"])
        image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(result["photo_id"]))
        return {
            "photo": image,
            "ingredients": "".join(result["ingredients"]),
            "name": result["name"]
        }

class Clicker:
    @staticmethod
    @inject
    async def on_like(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService], 
    ):
        result = dialog_manager.start_data["temporal_recipes"].pop(-1)
        dialog_manager.start_data["recipe"].append(result)
        await dialog_manager.next()

    @staticmethod
    @inject
    async def on_dislike(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
    ):
        dialog_manager.start_data["temporal_recipes"].pop(-1)
        
    @staticmethod
    @inject
    async def on_last_like(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[FitnessService], 
    ):
        recipe = dialog_manager.start_data["temporal_recipes"].pop(-1)
        recipes: list[Recipe] = dialog_manager.start_data["recipe"]
        recipes.append(recipe)
        await service.make_day_menu(
            MakeDayMenuCommand(
                callback.from_user.id,
                recipes,
                False
            )
        )
        dialog_manager.start_data["temporal_recipes"].clear()
        dialog_manager.start_data["recipe"].clear()
        await dialog_manager.next()

    @staticmethod
    @inject
    async def on_last_like_my_snack(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[FitnessService], 
    ):
        dialog_manager.start_data["temporal_recipes"].pop(-1)
        recipes: list[Recipe] = dialog_manager.start_data["recipe"]
        snak_kkal = await service.make_day_menu(
            MakeDayMenuCommand(
                callback.from_user.id,
                recipes,
                True
            )
        )
        dialog_manager.dialog_data["snack_kkal"] = snak_kkal
        dialog_manager.start_data["temporal_recipes"].clear()
        dialog_manager.start_data["recipe"].clear()
        await dialog_manager.switch_to(
            DayMenuDialog.end_my_snack,
            show_mode=ShowMode.EDIT
        )

    @staticmethod
    @inject
    async def on_main(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
    ):
        dialog_manager.start_data["temporal_recipes"].clear()
        dialog_manager.start_data["recipe"].clear()
        await dialog_manager.start(
            PaidStartingDialog.start,
            data={
                "user_id": callback.from_user.id,
                "training": [],
                "food": []
            },
            show_mode=ShowMode.EDIT,
            mode=StartMode.NEW_STACK
        )


async def get_calc_kkal(
    dialog_manager: DialogManager,
    **kwargs
):
    return {"сalc_kkal": dialog_manager.dialog_data["snack_kkal"]}


day_menu_dialog = Dialog(
    Window(
        DynamicMedia("photo"),
        text.Format(
            "Название: {name}\nИнгредиенты:\n{ingredients}\nВыберите все блюда на день, и я напишу рецепты\nНравится этот завтрак или прислать другой?"
        ),
        kbd.Button(
            text.Const("☑️ Этот завтрак"),
            id="s_1",
            on_click=Clicker.on_like
        ),
        kbd.Button(
            text.Const("🔄 Другой завтрак"),
            id="s_11",
            on_click=Clicker.on_dislike
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="s_111",
            on_click=Clicker.on_main
        ),
        state=DayMenuDialog.breakfast,
        getter=Getter.get_breakfast,
    ),
    Window(
        DynamicMedia("photo"),
        text.Format(
            "Название: {name}\nИнгредиенты:\n{ingredients}\nВыберите все блюда на день, и я напишу рецепты\nНравится этот обед или прислать другой?"
        ),
        kbd.Button(
            text.Const("☑️ Этот обед"),
            id="s_2",
            on_click=Clicker.on_like
        ),
        kbd.Button(
            text.Const("🔄 Другой обeд"),
            id="s_22",
            on_click=Clicker.on_dislike
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="s_222",
            on_click=Clicker.on_main
        ),
        state=DayMenuDialog.lunch,
        getter=Getter.get_lunch,
    ),
    Window(
        DynamicMedia("photo"),
        text.Format(
            "Название: {name}\nИнгредиенты:\n{ingredients}\nВыберите все блюда на день, и я напишу рецепты\nНравится этот ужин или прислать другой?"
        ),
        kbd.Button(
            text.Const("☑️ Этот ужин"),
            id="s_3",
            on_click=Clicker.on_like
        ),
        kbd.Button(
            text.Const("🔄 Другой ужин"),
            id="s_33",
            on_click=Clicker.on_dislike
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="s_333",
            on_click=Clicker.on_main
        ),
        state=DayMenuDialog.dinner,
        getter=Getter.get_dinner,
    ),
    Window(
        DynamicMedia("photo"),
        text.Format(
            "Название: {name}\nИнгредиенты:\n{ingredients}\nВыберите все блюда на день, и я напишу рецепты\nНравится этот перекус или прислать другой?\n\nЕсли никакой не подходит, нажмите 'Свой перекус', и я напишу вам, сколько кбжу нужно добрать."
        ),
        kbd.Button(
            text.Const("☑️ Этот перекус"),
            id="s_4",
            on_click=Clicker.on_last_like
        ),
        kbd.Button(
            text.Const("🔄 Другой перекус"),
            id="s_44",
            on_click=Clicker.on_dislike
        ),
        kbd.Button(
            text.Const("☑️ Свой перекус"),
            id="s_444",
            on_click=Clicker.on_last_like_my_snack
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="s_4444",
            on_click=Clicker.on_main
        ),
        state=DayMenuDialog.snack,
        getter=Getter.get_snack,
    ),
    Window(
        text.Format(
            "Меню на сегодня сформировано.\nПерейдите в главное меню - /start, чтобы посомтреть его ✨"
        ),
        state=DayMenuDialog.end,
        
    ),
    Window(
        text.Format(
            "Меню на сегодня сформировано\nВам нужно добавить любой перекус, чтобы постараться добрать\nКалорий - {сalc_kkal}\nПерейдите в главное меню - /start, чтобы посомтреть его ✨"
        ),
        state=DayMenuDialog.end_my_snack,
        getter=get_calc_kkal
    ),
)