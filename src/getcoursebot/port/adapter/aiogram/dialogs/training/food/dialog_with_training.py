import operator
from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets import text, kbd, input

from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_helpers import Getter, Clicker
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import TrainingDialog


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
            kbd.Cancel(text.Const("⬅️ На главную"))
        ),
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
    )
)

# ~F