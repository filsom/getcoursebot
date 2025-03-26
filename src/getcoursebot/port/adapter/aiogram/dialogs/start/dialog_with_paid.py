from aiogram import F
from aiogram_dialog import Dialog, DialogManager, LaunchMode, ShowMode, StartMode, Window
from aiogram_dialog.widgets import kbd, text
from aiogram_dialog.widgets.media import DynamicMedia
from getcoursebot.domain.model.user import IDRole
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_states import PaidStartingDialog
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_helpers import Clicker, Getter


async def get_roles(dialog_manager: DialogManager, **kwargs):
    if IDRole.Admin in dialog_manager.start_data.get("roles"):
        return {"roles": True}
    return {"roles": False}


paid_starting_dialog = Dialog(
    Window(
        text.Const("Что будем делать? 👇🏻"),
        kbd.Column(
            kbd.Button(
                text.Const("Тренироваться"),
                id="training",
                on_click=Clicker.on_training,
            ),
            kbd.Button(
                text.Const("Кушать"),
                id="food",
                on_click=Clicker.on_food,
            ),
            kbd.Button(
                text.Const("Мое меню"), 
                id="my_day_menu",
                on_click=Clicker.on_my_meny,
            ),
        ),
        state=PaidStartingDialog.start,
    ),
    Window(
        text.Format("Вам недоступен этот раздел.\nВыберите другой 👇🏻"),
        kbd.Column(
            kbd.Button(
                text.Const("Тренироваться"), 
                id="training_id", 
                when=F["training"],
                on_click=Clicker.on_training
            ),
            kbd.Button(
                text.Const("Кушать"), 
                id="food_id", 
                when=F["food"],
                on_click=Clicker.on_food,
            ),
            kbd.Back(
                text.Const("⬅️ На главную"), 
                id="back_main"
            ),
        ),
        state=PaidStartingDialog.not_access,
        getter=Getter.get_kbd_status
    ),
    Window(
        text.Const("Меню на день не сфомировано.", when=~F["menu"]),
        DynamicMedia("photo", when=F["menu"]),
        text.Format(
            "{title}{ingredients}{text}",
            when=F["menu"]
        ),
        kbd.StubScroll(
            id="stub_scroll_1",
            pages="pages"
        ),
        kbd.NumberedPager(scroll="stub_scroll_1", when=~F["menu"]),
        kbd.SwitchTo(
            text.Const("⬅️ На главную"), 
            id="back_main_1", 
            state=PaidStartingDialog.start,
        ),
        state=PaidStartingDialog.menu,
        getter=Getter.get_paging_menu
    ),
    launch_mode=LaunchMode.ROOT
)