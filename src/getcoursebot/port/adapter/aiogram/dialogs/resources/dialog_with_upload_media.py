from aiogram import F, Bot, types as t
from aiogram.enums import ContentType 
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd, input
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.media import DynamicMedia

from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import UploadMediaDialog


async def on_delete(
    callback: t.CallbackQuery, 
    widget,
    dialog_manager: DialogManager,
):
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("media", [])
    del photos[media_number]
    if media_number > 0:
        await scroll.set_page(media_number - 1)


async def input_media_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    last_id = dialog_manager.current_stack().last_message_id
    await bot.delete_message(message.from_user.id, last_id)
    if message.content_type == ContentType.VIDEO:
        file_id = message.video.file_id
        file_unique_id = message.video.file_unique_id
        dialog_manager.dialog_data["content_type"] = ContentType.VIDEO
    elif message.content_type == ContentType.PHOTO:
        file_id = message.photo[-1].file_id
        file_unique_id = message.photo[-1].file_unique_id
        dialog_manager.dialog_data["content_type"] = ContentType.PHOTO
    metadata = (file_id, file_unique_id)
    dialog_manager.dialog_data.setdefault("media", []).append(metadata)
    dialog_manager.dialog_data.setdefault("data_media", []).append({
        "file_id": file_id,
        "file_unique_id": file_unique_id,
        "message_id": message.message_id,
        "content_type": message.content_type
    })
    await message.delete()
    dialog_manager.dialog_data.setdefault("preview_messages", [])


async def get_upload_media(dialog_manager: DialogManager, **kwargs) -> dict:
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("media", [])
    if photos:
        photo = photos[media_number]
        media = MediaAttachment(
            type=dialog_manager.dialog_data["content_type"],
            file_id=MediaId(*photo),
        )
        
    else:
        media = MediaAttachment(
            url="https://2dbags.co/wp-content/uploads/revslider/lookbook1-demo_slider/placeholder-38329_1080x675.jpg",
            type=ContentType.PHOTO,
        )
    return {
        "media_count": len(photos),
        "media_number": media_number + 1,
        "media": media,
    }


async def input_text_handler(
    message: t.Message, 
    source, 
    dialog_manager: DialogManager, 
    _
):
    await message.delete()
    dialog_manager.dialog_data["media_text"] = message.html_text
    dialog_manager.dialog_data["is_send_me"] = False
    message_id = dialog_manager.current_stack().last_message_id
    bot: Bot = dialog_manager.middleware_data["bot"]
    await bot.delete_message(message.from_user.id, message_id)
    await dialog_manager.next()


async def get_media_text(
    dialog_manager: DialogManager, 
    **kwargs
):
    return {
        "media_text": dialog_manager.dialog_data["media_text"],
        "is_send_me": dialog_manager.dialog_data.get("is_send_me", False)
    }


async def on_click_send_me(
    callback: t.CallbackQuery, 
    widget,
    dialog_manager: DialogManager,
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    bot: Bot = dialog_manager.middleware_data["bot"]
    builder = MediaGroupBuilder()
    inline_builder = InlineKeyboardBuilder()
    inline_builder.button(text="Все тренировки", callback_data="from_mailing")
    for media in dialog_manager.dialog_data["data_media"]:
        builder.add(type=media["content_type"], media=media["file_id"])
    messages = await bot.send_media_group(callback.from_user.id, media=builder.build())
    list_delete_message = []
    for message in messages:
        list_delete_message.append(message.message_id)
    text_message = await bot.send_message(
        callback.from_user.id, 
        dialog_manager.dialog_data["media_text"],
        reply_markup=inline_builder.as_markup(resize_keyboard=True)
    )
    list_delete_message.append(text_message.message_id)
    dialog_manager.dialog_data["preview_messages"].extend(list_delete_message)
    dialog_manager.dialog_data["is_send_me"] = True


async def on_click_success(
    callback: t.CallbackQuery, 
    widget,
    dialog_manager: DialogManager,
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    if len(dialog_manager.dialog_data.get("preview_messages")) != 0:
        await bot.delete_messages(
            callback.from_user.id,
            dialog_manager.dialog_data["preview_messages"]
        )
        dialog_manager.dialog_data["preview_messages"].clear()
    await dialog_manager.done(
        result= {
            "media": dialog_manager.dialog_data["media"],
            "inpute_text_media": dialog_manager.dialog_data["media_text"]
        },
        show_mode=ShowMode.EDIT
    )


upload_media_dialog = Dialog(
    Window(
        text.Const("Добавьте media группу.", when=F["media_count"] == 0),
        DynamicMedia(selector="media"),
        kbd.StubScroll(id="pages", pages="media_count"),
        kbd.Group(
            kbd.NumberedPager(
                scroll="pages", 
                when=F["pages"] > 1,
                current_page_text=text.Format("🔎")),
                width=5
            ),
        kbd.Column(
            kbd.Button(
                text.Format("Удалить"),
                id="delete_media_id",
                when="media_count",
                on_click=on_delete
            ),
            kbd.Button(
                text.Format("Добавить текст 📝"),
                id="confirm",
                when="media_count",
                on_click=kbd.Next(),
            )
        ),
        input.MessageInput(
            content_types=[ContentType.VIDEO, ContentType.PHOTO],
            func=input_media_handler
        ),
        getter=get_upload_media,
        state=UploadMediaDialog.start,
    ),
    Window(
        text.Const("Введите описание для media группы."),
        input.TextInput(id="inpute_text_media", on_success=input_text_handler),
        state=UploadMediaDialog.text
    ),
    Window(
        text.Multi(
            text.Format(
                "Проверьте добавленное описаниие media группы. 👇\n\n"
                "{media_text}\n",
                when=~F["is_send_me"]
            ),
            text.Const(
                "Сообщение для рассылки 👆\nНе переходите по кнопке, произойдет сброс состояния❗️\n",
                when=F["is_send_me"]
            ),
            text.Const("⬅️ - Отредактировать текст\n✅ - Успешно завершить",)
        ),
        kbd.Row(
            kbd.Back(text=text.Const("⬅️")),
            kbd.Button(
                text=text.Const("✅"), 
                id="add", 
                on_click=on_click_success
            ),
        ),
        kbd.Button(
            text.Const("Посмотреть"),
            id="send_me",
            on_click=on_click_send_me
        ),
        state=UploadMediaDialog.view,
        getter=get_media_text
    ),
)
