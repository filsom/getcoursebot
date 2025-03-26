from aiogram import F, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import kbd, text, input
from getcoursebot.domain.model.user import NameRole
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_helpers import (
    Clicker,
    Getter,
    delete_message_handler,
    inpute_email_handler,
    process_result_handler
)
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_states import (
    EmailInputeDialog, 
    FreeStartingDialog, 
    TrySubDialog
)


email_inpute_dialog = Dialog(
    Window(
        text.Const(
            "Важно ☝🏻\n\n"
            "Если вы являетесь участником групп GetCourse,\n"
            "Обязательно сравните правильность ввода @e-mail\n"
            "c Вашим профилем!"
        ),
        kbd.Cancel(text.Const("Отмена")),
        input.MessageInput(inpute_email_handler),
        state=EmailInputeDialog.start
    ),
    Window(
        text.Format("Ваш @e-mail адрес - {email}, введен верно?"),
        kbd.Row(
            kbd.Back(text.Const("Нет")),
            kbd.Button(text.Const("Да"), id="Yes", on_click=Clicker.on_confirmed_email)
        ),
        state=EmailInputeDialog.confirmed,
        getter=Getter.get_inputed_email,
    )
)


free_starting_dialog = Dialog(
    Window(
        text.Multi(
            text.Const("Здравствуйте. Пожалуйста, введите ваш email 👇🏻", when=~F["email"]),
            text.Format(
                "Приветсвую 👋🏻\n\nВаш @e-mail - {email}\n"
                "Активирована бесплатная подписка.\n\nВам будут приходить новые тренировки в этот чат, когда Мила их будет записывать ❤️",
                when=F["email"]
            ),
            text.Const("\n\nПолучить видеотренировку 👇🏻", when=F["on_view"])
        ),
        kbd.Group(
            kbd.Start(
                text.Const("Ввести @e-mail"), 
                id="email_input", 
                state=EmailInputeDialog.start,
                when=~F["email"]
            ),
            kbd.Button(
                text.Format("Бесплатная тренировка 🌟"), 
                id="view", on_click=Clicker.on_view_video, 
                when=F["on_view"]
            ),
            kbd.Button(
                text.Const("Я оплатила"),
                id='paid',
                on_click=Clicker.on_paid,
                when=F["email"]
            ),
        ),
        state=FreeStartingDialog.start,
        getter=Getter.get_email_and_roles
    ),
    on_process_result=process_result_handler
)


try_sub_dialog = Dialog(
    Window(
        text.Const(
            "Получите доступ ко всей базе 200+ тренировок\n"
            "и конструктору индивидуального меню,\n"
            "занимайтесь дома в удобное время и питайтесь правильно без подсчета калорий!\n\n"
            "Подробнее по ссылке https://workoutmila.ru/bot_payment"
        ),
        kbd.Column(
            kbd.Button(text.Const("Проверить доступ"), id="access", on_click=Clicker.on_access),
        ),
        state=TrySubDialog.start,
    ),
    Window(
        text.Const(
            "Пока не вижу вашу оплату. Обычно данные обновляются в течение часа.\n"
            "Вы можете нажать кнопку ниже чуть позже, чтобы снова проверить подписку.\n"
            "Если доступ не появляется, напишите нам @Workout_mila_bot"
        ),
        kbd.Cancel(text.Const("⬅️ На главную")),
        state=TrySubDialog.paid
    ),
    getter=Getter.get_user_roles
)