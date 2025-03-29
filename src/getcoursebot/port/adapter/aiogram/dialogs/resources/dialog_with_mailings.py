import asyncio
import operator
from typing import AsyncGenerator
from uuid import uuid4
from aiogram import F, Bot, types as t
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sqlalchemy.ext.asyncio import AsyncEngine

from getcoursebot.application.error import AlreadyProcessMailing
from getcoursebot.domain.model.training import RecipientMailing, StatusMailing
from getcoursebot.port.adapter.aiogram.dialogs.mailing_service import TelegramMailingService
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import AdminStartingDialog, SendMailingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import UploadMediaDialog


class MaillingDialog(StatesGroup):
    start = State()
    user = State()


class SendDialog(StatesGroup):
    start = State()


class PlandeMaillingDialog(StatesGroup):
    start = State()
    menu = State()
    end = State()



def make_inline_kbd(event_mailing):
    builder = InlineKeyboardBuilder()
    if event_mailing == RecipientMailing.TRAINING:
        builder.button(text="Все тренировки", callback_data="from_mailing")
        return builder.as_markup(resize_keyboard=True)
    return None


@inject
async def on_click_send_now_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[TelegramMailingService],
    engine: FromDishka[AsyncGenerator[AsyncEngine, None]]
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    bot: Bot = dialog_manager.middleware_data["bot"]
    mailing_id = uuid4()
    type_recipient = int(dialog_manager.start_data["type_recipient"])
    await service.add_new_mailing(
        mailing_id,
        None,
        dialog_manager.start_data["inpute_text_media"][0],
        dialog_manager.start_data["media"],
        type_recipient,
        StatusMailing.AWAIT
    )
    try:
        task_mailing = await service.create_task_mailing(mailing_id)
        _ = asyncio.create_task(task_mailing(bot=bot, engine=engine))
        await dialog_manager.switch_to(
            SendMailingDialog.send_end,
            show_mode=ShowMode.EDIT
        )
    except AlreadyProcessMailing:
        dialog_manager.show_mode = ShowMode.EDIT
        dialog_manager.dialog_data["mailing_id"] = mailing_id
        dialog_manager.dialog_data["mailing_is_processed"] = True


async def on_click_name_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
):
    await dialog_manager.start(
        SendMailingDialog.start,
        data={
            "media": dialog_manager.dialog_data["media"],
            "inpute_text_media": dialog_manager.dialog_data["inpute_text_media"],
            "type_recipient": item_id
        },
        show_mode=ShowMode.EDIT
    )


async def get_data_mailings(
   dialog_manager: DialogManager,
   **kwargs 
):
    name_mailings = [
        ("Бесплатные", RecipientMailing.FREE),
        ("Платные", RecipientMailing.PAID)
    ]
    return {"mailings": name_mailings}


@inject
async def input_name_mailing_handler(
    message: t.Message, 
    source, 
    dialog_manager: DialogManager, 
    _,
    service: FromDishka[TelegramMailingService],
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    message_id = dialog_manager.current_stack().last_message_id
    await bot.delete_message(message.from_user.id, message_id)
    await message.delete()
    list_file_ids = []
    for media in dialog_manager.start_data["media"]:
        list_file_ids.append(media["file_id"])
    if dialog_manager.dialog_data.get("mailing_is_processed", None) is True:
        await service.update_name_mailing(
            dialog_manager.dialog_data["mailing_id"],
            message.text.lower()
        )
    else:
        await service.add_new_mailing(
            uuid4(),
            message.text.lower(),
            dialog_manager.start_data["inpute_text_media"][0],
            dialog_manager.start_data["media"],
            int(dialog_manager.start_data["type_recipient"]),
            StatusMailing.AWAIT
        )
    await dialog_manager.next()


async def on_click_back_main(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    await dialog_manager.start(
        AdminStartingDialog.start,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )


async def get_processed_mailing(
    dialog_manager: DialogManager,
    **kwrags
):
    return {"mailing_is_processed": dialog_manager.dialog_data.get("mailing_is_processed", None)}
    

send_mailings_dialog = Dialog(
    Window(
        text.Multi(
            text.Const("Когда запустить рассылку? 🕑", when=~F["mailing_is_processed"]),
            text.Const("Есть запущенная рассылка, запланируйте эту.", when=F["mailing_is_processed"]),
        ),
        kbd.Row(
            kbd.Button(
                text.Const("Сейчас"),
                id="now_mailing",
                on_click=on_click_send_now_mailing,
                when=~F["mailing_is_processed"]
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
        ),
        getter=get_processed_mailing,
        state=SendMailingDialog.start
    ),
    Window(
        text.Const("Введите название рассылки (128 символов)."),
        input.TextInput(id="input_name_mailing", on_success=input_name_mailing_handler),
        state=SendMailingDialog.text
    ),
    Window(
        text.Const("Рассылка запланирована ✅"),
        kbd.Button(
            text.Const("⬅️ На главную"),
            id="back_main_from_mailing_1",
            on_click=on_click_back_main
        ),
        state=SendMailingDialog.plan_end
    ),
    Window(
        text.Const("Рассылка в процессе выполнения ✅"),
        kbd.Button(
            text.Const("⬅️ На главную"),
            id="back_main_from_mailing_2",
            on_click=on_click_back_main
        ),
        state=SendMailingDialog.send_end
    )
)


async def on_click_new_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        UploadMediaDialog.start,
        show_mode=ShowMode.EDIT,
        data={}
    )


async def process_result_add_new_mailing(
    start_data,
    result,
    dialog_manager: DialogManager,
):
    if result:
        dialog_manager.dialog_data["media"] = *result["media"],
        dialog_manager.dialog_data["inpute_text_media"] = result["inpute_text_media"],
        await dialog_manager.next(ShowMode.EDIT)


mailing_dialog = Dialog(
    Window(
        text.Const("Меню рассылки."),
        kbd.Button(
            text.Const("Новая рассылка"), 
            id="new_mailing", 
            on_click=on_click_new_mailing
        ),
        kbd.Start(
            text.Const("Запланированные"),
            id="planed_mailing",
            state=PlandeMaillingDialog.start,
            show_mode=ShowMode.EDIT,
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="back_main_from_mailling_menu",
        ),
        on_process_result=process_result_add_new_mailing,
        state=MaillingDialog.start
    ),
    Window(
        text.Const("Выберите категорию пользователей для рассылки."),
        kbd.Select(
            text.Format("{item[0]}"),
            id="s_name_mailing",
            item_id_getter=operator.itemgetter(1),
            items="mailings",
            on_click=on_click_name_mailing
        ),
        getter=get_data_mailings,
        state=MaillingDialog.user
    )
)


@inject
async def get_name_mailings(
    dialog_manager: DialogManager,
    service: FromDishka[QueryService], 
    **kwargs
):
    return await service.query_mailings_name()
    

@inject
async def on_click_name_plan_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
    service: FromDishka[QueryService], 
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    bot: Bot = dialog_manager.middleware_data["bot"]
    dialog_manager.dialog_data["mailing_id"] = item_id
    data_mailing = await service.query_mailing_with_id(item_id)
    dialog_manager.dialog_data["data_mailing"] = data_mailing
    builder = MediaGroupBuilder()
    for media in data_mailing["media"]:
        builder.add(type=media[1], media=media[0])
    media_messages = await bot.send_media_group(
        callback.from_user.id,
        media=builder.build()
    )
    list_delete_media = []
    for media_message in media_messages:
        list_delete_media.append(media_message.message_id)
    message = await bot.send_message(
        callback.from_user.id,
        data_mailing["text"]
    )
    list_delete_media.append(message.message_id)
    dialog_manager.dialog_data["preview_plan_mailing"] = list_delete_media
    await dialog_manager.next()


@inject
async def on_click_process_sending(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService], 
):
    await service.update_status_mailing(
        dialog_manager.dialog_data["mailing_id"],
        StatusMailing.PROCESS
    )


@inject
async def on_click_delete_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[TelegramMailingService], 
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    await service.delete_mailing(
        dialog_manager.dialog_data["mailing_id"]
    )
    await bot.delete_messages(
        callback.from_user.id,
        dialog_manager.dialog_data["preview_plan_mailing"]
    )
    await dialog_manager.done()


@inject
async def on_click_start_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[TelegramMailingService], 
    engine: FromDishka[AsyncGenerator[AsyncEngine, None]]
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    try:
        mailing_task = await service.create_task_mailing(
            dialog_manager.dialog_data["mailing_id"]
        )
        _ = asyncio.create_task(mailing_task(bot=bot, engine=engine))
        if dialog_manager.dialog_data.get("preview_plan_mailing", None) is not None:
            await bot.delete_messages(
                callback.from_user.id,
                dialog_manager.dialog_data["preview_plan_mailing"]
            )
        dialog_manager.dialog_data["result_text"] = "Рассылка успещно запущена."
    except AlreadyProcessMailing:
            dialog_manager.dialog_data["result_text"] = "Не удалось запустить рассылку, так как есть рассылка в процессе выполнения."
    await dialog_manager.next()


async def get_result_text(
    dialog_manager: DialogManager,
    **kwargs
):
    return {
        "result_text": dialog_manager.dialog_data.get("result_text", None)
    }


async def on_click_cancel_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    if dialog_manager.dialog_data.get("preview_plan_mailing", None) is not None:
        await bot.delete_messages(
            callback.from_user.id,
            dialog_manager.dialog_data["preview_plan_mailing"]
        )
    


planed_mailling_dialog = Dialog(
    Window(
        text.Const("Выберите запланированную рассылку 👇🏻"),
        kbd.Column(kbd.Select(
            text.Format("{item[0]}"),
            id="s_planed_mailling",
            item_id_getter=operator.itemgetter(1),
            items="plan_mailings",
            on_click=on_click_name_plan_mailing
        )),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_planed_mailling",
        ),
        getter=get_name_mailings,
        state=PlandeMaillingDialog.start
    ),
    Window(
        text.Const("Сообщение для рассылки 👆🏻"),
        kbd.Row(
            kbd.Button(
                text.Const("Удалить"),
                id="process_delete",
                on_click=on_click_delete_mailing
            ),
            kbd.Button(
                text.Const("Запустить 🔔"),
                id="process_sending",
                on_click=on_click_start_mailing
            ),
        ),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_planed_mailling_1",
            on_click=on_click_cancel_mailing
        ),
        getter=get_name_mailings,
        state=PlandeMaillingDialog.menu
    ),
    Window(
        text.Format("{result_text}"),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_planed_mailling_1",
            on_click=on_click_cancel_mailing
        ),
        getter=get_result_text,
        state=PlandeMaillingDialog.end
    )  
)