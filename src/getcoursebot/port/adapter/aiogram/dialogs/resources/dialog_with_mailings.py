import asyncio
from aiogram import Bot, types as t
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets import text, kbd, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService


            # "user_id": callback.from_user.id, 
            # "media": dialog_manager.dialog_data["media"], [{}, {}]
            # "inpute_text_media": dialog_manager.dialog_data["media_text"]

            # "file_id": file_id,
            # "file_unique_id": file_unique_id,
            # "message_id": message.message_id,
            # "content_type": message.content_type


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


async def on_click_now_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    users_ids = await service.query_users()


free_mailings_dialog = Dialog(
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
                on_click=...
            )
        )
    ),
    Window()
)