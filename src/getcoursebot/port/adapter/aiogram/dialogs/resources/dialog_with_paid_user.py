from aiogram import F, types as t
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.domain.model.access import AccessGC, Group
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import PaidStartingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import FoodDialog, TrainingDialog, WithDataDialog


async def get_kbd_status(dialog_manager: DialogManager, **kwargs):         
    return {
        "training": dialog_manager.dialog_data["training"],
        "food": dialog_manager.dialog_data["food"]
    }

@inject
async def on_сlick_training(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    access_user = await service.query_user_roles(callback.from_user.id)
    if access_user.check_group(Group.TRAINING):
        await dialog_manager.start(
            TrainingDialog.start,
            data={
                "user_id": callback.from_user.id,
                "groups": access_user.groups,
            }
        )
    else:
        dialog_manager.dialog_data["training"] = False
        dialog_manager.dialog_data["food"] = True
        await dialog_manager.next()


@inject
async def on_сlick_food(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    access_user = await service.query_user_roles(callback.from_user.id)
    if access_user.check_group(Group.FOOD):
        await dialog_manager.start(
            FoodDialog.start,
            data={
                "groups": access_user.groups,
                "user_id": callback.from_user.id
            }
        )
    else:
        dialog_manager.dialog_data["training"] = True
        dialog_manager.dialog_data["food"] = False
        await dialog_manager.next()


paid_starting_dialog = Dialog(
    Window(
        text.Const("Что будем делать? 👇🏻"),
        kbd.Column(
            kbd.Button(
                text.Const("Тренироваться"),
                id="training",
                on_click=on_сlick_training,
            ),
            kbd.Button(
                text.Const("Кушать"),
                id="food",
                on_click=on_сlick_food,
            ),
        ),
        state=PaidStartingDialog.start
    ),
    Window(
        text.Format("Вам недоступен этот раздел.\nВыберите другой 👇🏻"),
        kbd.Column(
            kbd.Button(
                text.Const("Тренироваться"), 
                id="next_training", 
                when=F["training"],
                on_click=on_сlick_training
            ),
            kbd.Button(
                text.Const("Кушать"), 
                id="next_food", 
                when=F["food"],
                on_click=on_сlick_food,
            ),
            kbd.Back(
                text.Const("⬅️ На главную"), 
                id="back_main"
            ),
        ),
        state=PaidStartingDialog.not_access,
        getter=get_kbd_status
    ),
)