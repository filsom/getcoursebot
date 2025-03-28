import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.types import CallbackQuery, Message

from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, NumberedPager, StubScroll
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format


class Medias(StatesGroup):
    start = State()


async def on_input_photo(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
):
    x = dialog_manager.current_stack().last_message_id
    b: Bot = dialog_manager.middleware_data["bot"]
    await b.delete_message(message.from_user.id, x)
    if message.content_type == ContentType.VIDEO:
        metadata = (message.video.file_id, message.video.file_unique_id)
        dialog_manager.dialog_data["content_type"] = ContentType.VIDEO
    elif message.content_type == ContentType.PHOTO:
        metadata = (message.photo[-1].file_id, message.photo[-1].file_unique_id)
        dialog_manager.dialog_data["content_type"] = ContentType.PHOTO
    dialog_manager.dialog_data.setdefault("media", []).append(metadata)
    await message.delete()

async def on_delete(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager,
):
    scroll: ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("media", [])
    del photos[media_number]
    if media_number > 0:
        await scroll.set_page(media_number - 1)


async def getter(dialog_manager: DialogManager, **kwargs) -> dict:
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


dialog = Dialog(Window(
    Const("Send media"),
    DynamicMedia(selector="media"),
    StubScroll(id="pages", pages="media_count"),
    Group(
        NumberedPager(scroll="pages", when=F["pages"] > 1),
        width=8,
    ),
    Button(
        Format("🗑️ Delete photo #{media_number}"),
        id="del",
        on_click=on_delete,
        when="media_count",
        # Alternative F['media_count']
    ),
    MessageInput(content_types=[ContentType.VIDEO, ContentType.PHOTO], func=on_input_photo),
    getter=getter,
    state=Medias.start,
))


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(Medias.start, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot("7682965504:AAEX7p2SPM_Kq8ZRsg-1L9nuNnqATvL6h_I")
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dp.include_router(dialog)

    dp.message.register(start, CommandStart())
    setup_dialogs(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())