import asyncio
import operator
from aiogram import Bot, types as t
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import AdminStartingDialog


class EventMailing(object):
    TRAINING = 1
    FREE = 2
    PAID = 3


async def send_mailing_message(
    users_ids: list[int],
    mailing_media: list[dict],
    mailing_text: str,
    kbd,
    bot: Bot
):
    builder = MediaGroupBuilder()
    for media in mailing_media:
        builder.add(
           type=media["content_type"],
           media=media["file_id"]
        )
    media_messages = builder.build()
    try:
        for user_id in users_ids:
            await bot.send_media_group(user_id, media_messages)
            await bot.send_message(user_id, mailing_text, reply_markup=kbd)
            await asyncio.sleep(0.5)
    except Exception as err:
        print(err)


def make_inline_kbd(event_mailing):
    builder = InlineKeyboardBuilder()
    if event_mailing == EventMailing.TRAINING:
        builder.button(text="Все тренировки", callback_data="from_mailing")
        return builder.as_markup(resize_keyboard=True)
    return None


@inject
async def on_click_now_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    users_ids = await service.query_all_user_id_with_role()
    _ = asyncio.create_task(send_mailing_message(
        users_ids,
        dialog_manager.start_data["media"],
        dialog_manager.start_data["inpute_text_media"],
        make_inline_kbd( dialog_manager.start_data["event_mailing"]),
        bot
    ))
    await dialog_manager.done()


@inject
async def on_click_name_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
    service: FromDishka[QueryService]
):
    pass


async def get_data_mailings(
   dialog_manager: DialogManager,
   **kwargs 
):
    pass


@inject
async def input_name_mailing_handler(
    message: t.Message, 
    source, 
    dialog_manager: DialogManager, 
    service: FromDishka[FitnessService],
    _
):
    await message.delete()
    if len(message.text) > 128:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await message.answer("Некорректное название рассылки ❌")
    dialog_manager.dialog_data["name_mailing"] = message.text.lower()
    list_file_ids = []
    for media in dialog_manager.start_data["media"]:
        list_file_ids.append(media["file_id"])
    await service.add_new_mailling(
        list_file_ids,
        dialog_manager.start_data["inpute_text_media"],
        dialog_manager.start_data["media"][0]["content_type"],
        dialog_manager.start_data["event_mailing"]
    )
    await dialog_manager.next()


async def on_click_back_main(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        AdminStartingDialog.start,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT
    )
    

send_mailings_dialog = Dialog(
    Window(
        text.Const("Когда запустить рассылку? 🕑"),
        kbd.Row(
            kbd.Button(
                text.Const("Сейчас"),
                id="now_mailing",
                on_click=on_click_now_mailing
            ),
            kbd.Button(
                text.Const("Запланировать"),
                id="plan_mailing",
                on_click=kbd.Next()
            ),
            kbd.Button(
                text.Const("⬅️ На главную"),
                id="back_main_from_mailing",
                on_click=on_click_back_main
            )
        )
    ),
    Window(
        text.Const("Введите название рассылки (128 символов)."),
        input.TextInput(id="input_name_mailing", on_success=input_name_mailing_handler)
    ),
    Window(
        text.Const("Рассылка запланирована ✅"),
        kbd.Button(
            text.Const("⬅️ На главную"),
            id="back_main_from_mailing",
            on_click=on_click_back_main
        )
    )
)