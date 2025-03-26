import operator
from aiogram import F
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets import text, kbd, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_helpers import Getter, Clicker
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import TrainingDialog


async def on_confirm_previe_in_like(
    event,
    button, 
    dialog_manager: DialogManager, 
):
    dialog_manager.dialog_data["user_id"] = event.from_user.id
    await dialog_manager.switch_to(TrainingDialog.view_like)


@inject
async def on_confirm_preview_like(
    event,
    button, 
    dialog_manager: DialogManager, 
    service: FromDishka[QueryService]
):
    await service.delete_like_traioning(
        dialog_manager.dialog_data["training_id"]
    )
    


training_dialog = Dialog(
    Window(
        text.Const("Выберите категорию"),
        kbd.Column(
            kbd.Select(
                id="selected_categories",
                text=text.Format("{item[0]}"),
                items="categories",
                item_id_getter=operator.itemgetter(1),
                on_click=Clicker.on_category_name
            ),
        ),
        kbd.Button(text.Format("Из избраного ❤️"), id="is_like_videos", on_click=on_confirm_previe_in_like),
        kbd.Cancel(text.Const("⬅️ На главную")),
        state=TrainingDialog.start,
        getter=Getter.get_categories
    ),
    Window(
        text.Format("{text_training}"),
        kbd.Column(
            kbd.Button(
                text.Const("Добавить в избранное ❤️"), 
                id="like",
                when=~F["is_like"],
                on_click=Clicker.on_like,
            ),
            kbd.Button(text.Const("Заменить 🔄"), id="reply"),
            kbd.Back(text.Const("⬅️ К категориям"))
        ),
        state=TrainingDialog.view,
        getter=Getter.get_random_training
    ),
    Window(
        text.Format("{text_training}"),
        kbd.Button(text.Const("Удалить ❌"), id="reply_1", when=F["is_not"], on_click=on_confirm_preview_like),
        kbd.Button(text.Const("Заменить 🔄"), id="reply_12", when=F["is_not"]),
        kbd.Cancel(text.Const("⬅️ На главную")),
        state=TrainingDialog.view_like,
        getter=Getter.get_random_training_like
    ),
)

# ~F