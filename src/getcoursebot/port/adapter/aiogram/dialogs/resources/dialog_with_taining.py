import operator

from aiogram import F, Bot, types as t
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.application.commands import AddTrainingCommand
from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import SendMailingDialog
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_with_mailings import RecipientMailing
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import NewTrainingDialog, TrainingDialog, UploadMediaDialog


async def on_сlick_view_like_training(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["is_like_view"] = True
    dialog_manager.dialog_data["is_delete"] = True
    await dialog_manager.next()


# async def on_click_category_name(
#     callback: t.CallbackQuery,
#     button,
#     dialog_manager: DialogManager,
#     item_id,
# ):
#     dialog_manager.dialog_data["category_id"] = item_id
#     dialog_manager.dialog_data["user_id"] = callback.from_user.id
#     await dialog_manager.next()


async def on_click_category_name(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
):
    dialog_manager.dialog_data["category_id"] = item_id
    dialog_manager.dialog_data["user_id"] = callback.from_user.id
    await dialog_manager.start(
        UploadMediaDialog.start,
        show_mode=ShowMode.EDIT,
        data={"from_training": True}
    )


async def on_click_back_main(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["is_like_view"] = None
    dialog_manager.dialog_data["is_delete"] = None


@inject
async def on_click_like_training(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService], 
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    await service.insert_like(
        callback.from_user.id,
        dialog_manager.dialog_data["training_id"]
    )
    await bot.delete_messages(
        callback.from_user.id,
        dialog_manager.dialog_data.pop("list_messages")
    )


@inject
async def on_click_delete_like_training(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService], 
):
    await service.delete_like_training(
        dialog_manager.dialog_data["training_id"]
    )
    bot: Bot = dialog_manager.middleware_data["bot"]
    await bot.delete_messages(
        callback.from_user.id,
        dialog_manager.dialog_data.pop("list_messages")
    )


async def on_click_reply_training(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    await bot.delete_messages(
        callback.from_user.id,
        dialog_manager.dialog_data.pop("list_messages")
    )


@inject
async def get_random_training(
    dialog_manager: DialogManager,
    service: FromDishka[QueryService],
    **kwargs
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    training = await service.query_random_training(
        dialog_manager.dialog_data["category_id"],
        dialog_manager.dialog_data["user_id"],
        dialog_manager.dialog_data.get("is_like_view", False)
    )
    bot: Bot = dialog_manager.middleware_data["bot"]
    if training.get("message", None) is None:
        builder = MediaGroupBuilder()
        for video in training["videos"]:
            builder.add_video(video.file_id)

        dialog_manager.dialog_data["training_id"] = training["training_id"]
        messages = await bot.send_media_group(
            dialog_manager.dialog_data["user_id"], 
            media=builder.build()
        )
        list_messages = []
        for message in messages:
            list_messages.append(message.message_id)
        dialog_manager.dialog_data["list_messages"] = list_messages
        return {
            "text_training": training["text"],
            "is_like": training["is_like"],
            "is_delete": training["is_delete"]
        }
    else:
        await bot.send_message(
            dialog_manager.dialog_data["user_id"],
            training["message"]
        )
        await dialog_manager.done()


@inject
async def get_name_categories(
    dialog_manager: DialogManager, 
    service: FromDishka[QueryService], 
    **kwargs
):
    if dialog_manager.dialog_data.get("is_like_view", False) is True:
        return await service.query_categories(
            dialog_manager.start_data["user_id"]
        )
    else:
        return await service.query_categories()


trainings_dialog = Dialog(
    Window(
        text.Const("Выберите раздел"),
        kbd.Button(
            text.Const("Найти тренировку 🔎"),
            id="search_training",
            on_click=kbd.Next()
        ),
        kbd.Button(
            text.Const("Из избраного ❤️"),
            id="is_like_training",
            on_click=on_сlick_view_like_training
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="back_main_2",
        ),
        state=TrainingDialog.start
    ),
    Window(
        text.Const("Выберите категорию 👇🏻"),
        kbd.Column(
            kbd.Select(
                id="selected_categories",
                text=text.Format("{item[0]}"),
                items="categories",
                item_id_getter=operator.itemgetter(1),
                on_click=on_click_category_name
            ),
        ),
        kbd.Back(
            text.Const("⬅️ К категориям"),
            id="back_categories",
            on_click=on_click_back_main
        ),
        state=TrainingDialog.categories,
        getter=get_name_categories
    ),
    Window(
        text.Format("{text_training}"),
        kbd.Column(
            kbd.Button(
                text.Const("Добавить в избранное ❤️"), 
                id="like",
                when=F["is_like"],
                on_click=on_click_like_training,
            ),
            kbd.Button(
                text.Const("Заменить 🔄"), 
                id="reply",
                on_click=on_click_reply_training
            ),
            kbd.Button(
                text.Const("Удалить"), 
                id="delete",
                when=F["is_delete"],
                on_click=on_click_delete_like_training,
            ),
            kbd.Back(
                text.Const("⬅️ К категориям"),
                on_click=on_click_reply_training
            )
        ),
        state=TrainingDialog.view,
        getter=get_random_training
    )
)


@inject
async def get_categories_name(
    dialog_manager: DialogManager, 
    service: FromDishka[QueryService], 
    **kwargs
):
    return await service.query_categories()


@inject
async def process_result_add_training(
    start_data,
    result,
    dialog_manager: DialogManager,
    service: FromDishka[FitnessService]
):
    if result:
        dialog_manager.dialog_data["media"] = result["media"]
        dialog_manager.dialog_data["inpute_text_media"] = result["inpute_text_media"]
        await service.add_training(
            AddTrainingCommand(
                result["user_id"],
                dialog_manager.dialog_data["category_id"],
                result["inpute_text_media"],
                result["media"]
            )
        )
        await dialog_manager.next()


@inject
async def on_click_free_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        SendMailingDialog.start,
        data={
            "user_id": callback.from_user.id, 
            "media": dialog_manager.dialog_data["media"],
            "inpute_text_media": dialog_manager.dialog_data["inpute_text_media"],
            "type_recipient": RecipientMailing.TRAINING
        },
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT
    )


new_training_dialog = Dialog(
    Window(
        text.Const("Выберите категорию тренировки!"),
        kbd.Column(
            kbd.Select(
                id='id_name_training',
                text=text.Format("{item[0]}"),
                items="categories",
                item_id_getter=operator.itemgetter(1),
                on_click=on_click_category_name
            ),
        ),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main"),
        state=NewTrainingDialog.start,
        getter=get_categories_name,
        on_process_result=process_result_add_training
    ),
    Window(
        text.Const(
            "Тренировка успешно сохранена ✅\nРазослать бесплатным пользователям?"
        ),
        kbd.Row(
            kbd.Button(
                text.Const("Да"),
                id="yes_mailing",
                on_click=on_click_free_mailing
            ),
            kbd.Cancel(text.Const("Нет"))
        ),
        state=NewTrainingDialog.send,
    )
)