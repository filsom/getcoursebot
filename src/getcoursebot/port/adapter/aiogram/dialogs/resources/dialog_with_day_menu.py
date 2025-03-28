from aiogram import F, Bot, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import PaidStartingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import DayMenuDialog


async def get_user_norma_kkal(
    dialog_manager: DialogManager,
    **kwargs
):
    return {"kkal": dialog_manager.dialog_data.get("snack_kkal")}


@inject
async def get_data_recipe(
    dialog_manager: DialogManager,
    service: FromDishka[QueryService],
    **kwargs
):
    type_meal = dialog_manager.start_data["type_meal"][0]
    recipe_data = await service.query_recipe_with_type(type_meal)
    dialog_manager.dialog_data["temporal_recipes"] = recipe_data
    return recipe_data


@inject
async def on_click_like_recipe(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[FitnessService]
):
    dialog_manager.start_data["type_meal"].pop(0)
    like_recipe = dialog_manager.dialog_data["temporal_recipes"]
    bot: Bot = dialog_manager.middleware_data["bot"]
    message_photo = await bot.send_photo(callback.from_user.id, like_recipe["photo_id"])
    message = await bot.send_message(callback.from_user.id, like_recipe["name_ingredients"])
    dialog_manager.start_data["dirty_photos"].append(message_photo.message_id)
    dialog_manager.start_data["recipes"].update({
        like_recipe["recipe_id"]: message.message_id,
    })
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    if not dialog_manager.start_data["type_meal"]:
        list_recipes_ids = []
        for recipe_id in dialog_manager.start_data["recipes"]:
            list_recipes_ids.append(recipe_id)
        adjusted_recipes = await service.adjusted_recipes(
            list_recipes_ids,
            dialog_manager.start_data["norma_kkal"]["kkal"],
            False
        )
        for recipe in adjusted_recipes:
            message_id = dialog_manager.start_data["recipes"].get(recipe)
            if message_id is not None:
                await bot.edit_message_text(
                    adjusted_recipes[recipe],
                    chat_id=callback.from_user.id,
                    message_id=message_id
                )
        dialog_manager.start_data["dirty_photos"].clear()
        dialog_manager.start_data["recipes"].clear()
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()


@inject
async def on_click_my_snack(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[FitnessService]
):
    dialog_manager.start_data["type_meal"].clear()
    bot: Bot = dialog_manager.middleware_data["bot"]
    list_recipes_ids = []
    for recipe_id in dialog_manager.start_data["recipes"]:
        list_recipes_ids.append(recipe_id)
    
    adjusted_recipes = await service.adjusted_recipes(
        list_recipes_ids,
        dialog_manager.start_data["norma_kkal"]["kkal"],
        True
    )
    for recipe in adjusted_recipes:
        message_id = dialog_manager.start_data["recipes"].get(recipe)
        if message_id is not None:
            await bot.edit_message_text(
                adjusted_recipes[recipe],
                chat_id=callback.from_user.id,
                message_id=message_id
            )
    dialog_manager.start_data["dirty_photos"].clear()
    dialog_manager.dialog_data["snack_kkal"] = adjusted_recipes["amount_kkal"]
    dialog_manager.start_data["recipes"].clear()
    await dialog_manager.next()


@inject
async def on_click_back_main(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    if dialog_manager.start_data["recipes"]:
        bot: Bot = dialog_manager.middleware_data["bot"]
        list_delete_messages = []
        for message_id in dialog_manager.start_data["recipes"].values():
            if message_id is not None:
                list_delete_messages.append(message_id)
        list_delete_messages.extend(dialog_manager.start_data["dirty_photos"])
        await bot.delete_messages(callback.from_user.id, list_delete_messages)
    access_user = await service.query_user_roles(callback.from_user.id)
    await dialog_manager.start(
        PaidStartingDialog.start,
        data={
            "groups": access_user.groups,
            "user_id": callback.from_user.id
        },
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT
    )


day_menu_dialog = Dialog(
    Window(
        DynamicMedia("photo"),
        text.Format(
            "Ингредиенты:\n\n{name_ingredients}\n\n"
            "Выберите все блюда на день, и я напишу рецепты\n"
            "Нравится этот {name_meal} или прислать другой?"
        ),
        kbd.Button(
            text.Format("Этот {name_meal}"),
            id="like_meal",
            on_click=on_click_like_recipe
        ),
        kbd.Button(
            text.Format("Другой {name_meal}"),
            id="next_meal",
        ),
        kbd.Button(
            text.Format("Cвой {name_meal}"),
            id="my_snack",
            on_click=on_click_my_snack,
            when=F["is_my_snack"]
        ),
        kbd.Button(
            text.Const("⬅️ На главную"),
            id="back_main_from_day_menu",
            on_click=on_click_back_main
        ),
        state=DayMenuDialog.start,
        getter=get_data_recipe
    ),
    Window(
        text.Multi(
            text.Format(
                "Готовые рецепты с количеством ингредиентов выше 👆\n"
                "Вам нужно добавить любой перекус, чтобы постараться добрать.\n\n"
                "Калорий - {kkal}",
                when=F["kkal"]
            ),
            text.Const(
                "Готовые рецепты с количеством ингредиентов выше 👆",
                when=~F["kkal"]
            ),
        ),
        kbd.Button(
            text.Const("⬅️ На главную"),
            id="back_main_from_day_menu_1",
            on_click=on_click_back_main
        ),
        state=DayMenuDialog.view,
        getter=get_user_norma_kkal
    ),
)