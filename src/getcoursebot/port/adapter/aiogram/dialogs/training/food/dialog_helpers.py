from typing import TYPE_CHECKING
from aiogram import Bot, types as t
from aiogram_dialog import DialogManager, ShowMode
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram.enums import ContentType
from aiogram_dialog.widgets.common import ManagedScroll
from dishka.integrations.aiogram_dialog import inject
from dishka import FromDishka

from getcoursebot.application.commands import AddTrainingCommand
# from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.domain.model.training import Media
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService


class Clicker:
    @staticmethod
    @inject
    async def on_like(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService], 
    ):
        await service.insert_like(
            callback.from_user.id,
            dialog_manager.dialog_data["training_id"]
        )
        await callback.message.answer(
            "Тренировка добавлена в избранное."
        )

    @staticmethod
    async def on_delete_video(
        callback: t.CallbackQuery, 
        widget, 
        dialog_manager: DialogManager,
    ):
        scroll: ManagedScroll = dialog_manager.find("pages")
        media_number = await scroll.get_page()
        photos = dialog_manager.dialog_data.get("videos", [])
        del photos[media_number]
        if media_number > 0:
            await scroll.set_page(media_number - 1)
        
    @staticmethod
    @inject
    async def on_category_name(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        item_id,
    ):
        dialog_manager.dialog_data["category_id"] = item_id
        dialog_manager.dialog_data["user_id"] = callback.from_user.id
        await dialog_manager.next()

    @inject
    async def on_confirm_preview(
        event: t.CallbackQuery, 
        button, 
        dialog_manager: 
        DialogManager, 
        service: FromDishka[FitnessService]
    ):
        # (video[0], video[1], message.message_id, message.content_type)
        dialog_manager.show_mode = ShowMode.EDIT
        list_files = []
        for file_id in dialog_manager.dialog_data['videos']:
            list_files.append(Media(file_id[2], file_id[0], file_id[1], file_id[3]))
        await service.add_training(
            AddTrainingCommand(
                event.from_user.id,
                dialog_manager.dialog_data['category_id'],
                dialog_manager.find('text_training_1').get_value(),
                list_files
            )
        )
        await dialog_manager.next()

class Getter:
    @staticmethod
    @inject
    async def get_categories(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService], 
        **kwargs
    ):
        return await service.query_categories()
    
    @staticmethod
    @inject
    async def get_random_training(
        dialog_manager: DialogManager,
        service: FromDishka[QueryService],
        **kwargs
    ):
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        data = await service.query_training(
            dialog_manager.dialog_data["user_id"],
            dialog_manager.dialog_data["category_id"]
        )
        builder = MediaGroupBuilder()
        for video in sorted(data["training"].videos, key=lambda x: x.message_id):
            builder.add_video(video.file_id)

        dialog_manager.dialog_data["training_id"] = data["training"].training_id

        bot: Bot = dialog_manager.middleware_data["bot"]
        await bot.send_media_group(
            dialog_manager.dialog_data["user_id"], 
            media=builder.build()
        )
        return {
            "text_training": data["training"].text,
            "is_like": data["is_like"]
        }
        
    @staticmethod
    async def get_media_group_videos(dialog_manager: DialogManager, **kwargs) -> dict:
        scroll: ManagedScroll = dialog_manager.find("pages")
        media_number = await scroll.get_page()
        photos = dialog_manager.dialog_data.get("videos", [])
        if photos:
            photo = photos[media_number]
            media = MediaAttachment(
                file_id=MediaId(photo[0], photo[1]),
                type=ContentType.VIDEO,
            )
        else:
            media = MediaAttachment(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Image_not_available.png/800px-Image_not_available.png?20210219185637",
                type=ContentType.PHOTO,
            )
        return {
            "media_count": len(photos),
            "media_number": media_number + 1,
            "media": media,
        }
    
    async def get_text_training(
        dialog_manager: DialogManager, 
        **kwargs
    ):
        return {"text_training_1": dialog_manager.find("text_training_1").get_value()}
    

async def on_input_videos_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
):  
    await message.delete()
    keys_video = []
    for video in message.video:
        if video[0] == 'file_id':
            keys_video.append(video[1])
        if video[0] == 'file_unique_id':
            keys_video.append(video[1])
    for key_video in range(0, len(keys_video), 2):
        video = keys_video[key_video:key_video+2]
        dialog_manager.dialog_data.setdefault("videos", []).append(
            (video[0], video[1], message.message_id, message.content_type)
        )
    dialog_manager.dialog_data["videos"].sort(key=lambda x: x[2])
    dialog_manager.show_mode = ShowMode.EDIT


async def on_input_text_handler(
    message: t.Message, 
    source, 
    dialog_manager: DialogManager, 
    _
):
    await message.delete()
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.next()