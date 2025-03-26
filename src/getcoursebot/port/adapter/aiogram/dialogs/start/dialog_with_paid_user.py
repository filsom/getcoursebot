from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets import text, kbd, input





paid_starting_dialog = Dialog(
    Window(
        text.Const("Что будем делать? 👇🏻"),
        kbd.Column(
            kbd.Button(
                text.Const("Тренироваться"),
                id="training",
                on_click=...,
            ),
            kbd.Button(
                text.Const("Кушать"),
                id="food",
                on_click=...,
            ),
        ),
        state=...
    ),
)