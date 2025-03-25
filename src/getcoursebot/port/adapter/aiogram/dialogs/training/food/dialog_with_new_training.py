import operator

from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import input, text, kbd
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_with_mailling import MaillingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import (
    NewTrainingDialog
)
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_helpers import (
    Getter, 
    Clicker, 
    on_input_text_handler, 
    on_input_videos_handler
)
# class OnClickTraining:
#     @staticmethod
#     async def on_done_mailing(
#         event: CallbackQuery, button, dialog_manager: DialogManager
#     ):
#         await dialog_manager.done()

#     @staticmethod
#     async def on_input_text(
#         message: Message, source, dialog_manager: DialogManager, _
#     ):
#         await message.delete()
#         dialog_manager.show_mode = ShowMode.EDIT
#         await dialog_manager.next()

#     @staticmethod
#     @inject
#     async def on_click_send_mailling_free(
#         callback: CallbackQuery, widget, dialog_manager: DialogManager
#     ):
#         dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
#         bot: Bot = dialog_manager.middleware_data['bot']
#         list_ids = await service.query_user_ids_with_role([NameRole.Free])
#         builder = MediaGroupBuilder()
#         for video in dialog_manager.dialog_data['videos']:
#             builder.add_video(video[0])
#         xx = builder.build()
#         for id in list_ids:
#             await bot.send_media_group(id, xx)
#             await bot.send_message(
#                 id, 
#                 dialog_manager.find('text_training_1').get_value(),
#             )
#         await dialog_manager.next()

#     @staticmethod
#     async def on_click_not_send_mailling_free(
#         callback: CallbackQuery, widget, dialog_manager: DialogManager
#     ):
#         await dialog_manager.next()

#     @staticmethod
#     @inject
#     async def on_click_send_mailling_pay(
#         callback: CallbackQuery, widget, dialog_manager: DialogManager
#     ):
#         dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
#         bot: Bot = dialog_manager.middleware_data['bot']
#         list_ids = await service.query_user_ids_with_role([NameRole.Training])
#         builder = MediaGroupBuilder()
#         for video in dialog_manager.dialog_data['videos']:
#             builder.add_video(video[0])
#         xx = builder.build()
#         builder = InlineKeyboardBuilder()
#         builder.add(InlineKeyboardButton(text='Все тренировки', callback_data="all_training"))
#         for id in list_ids:
#             await bot.send_media_group(id, xx)
#             await bot.send_message(
#                 id, 
#                 dialog_manager.find('text_training_1').get_value(),
#                 reply_markup=builder.as_markup()
#             )
#         await dialog_manager.done()

#     @staticmethod
#     @inject
#     async def on_click_plan_send_mailling_pay(
#         callback: CallbackQuery, widget, dialog_manager: DialogManager, service: FromDishka[FitnessService]
#     ):
#         # Дописать!
#         await dialog_manager.done()


async def on_mailling_message(
    event,
    button, 
    dialog_manager: 
    DialogManager, 
):
    await dialog_manager.start(
        state=MaillingDialog.new_mall,
        data={
            "photos": dialog_manager.dialog_data['videos'],
            "text_mailling_mess": dialog_manager.find('text_training_1').get_value()
        },
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK
    )

new_training_dialog = Dialog(
    Window(
        Const("Выберите категорию тренировки!"),
        kbd.Column(
            kbd.Select(
                id='id_type_training',
                text=text.Format("{item[0]}"),
                items="categories",
                item_id_getter=operator.itemgetter(1),
                on_click=Clicker.on_category_name
            ),
        ),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main_228"),
        state=NewTrainingDialog.start,
        getter=Getter.get_categories
    ),
    Window(
        text.Format(
            "Отправьте видео с тренировками 📹\n\n"
            "При отправке видео <b>не</b> <b>добавляйте</b> описание к ним,\n"
            "описание тренировки, будет добавлено на соответствующем шаге❗️",
            when=F["media_count"] == 0
        ),
        DynamicMedia(selector="media"),
        kbd.StubScroll(id="pages", pages="media_count"),
        kbd.Group(
            kbd.NumberedPager(
                scroll="pages", 
                when=F["pages"] > 1, 
                page_text=Format("№{target_page1}"), 
                current_page_text=Format("🔎")), 
                width=2
            ),
        kbd.Column(
            kbd.Button(
                Format("Удалить видео №{media_number} 🗑️"),
                id="del",
                on_click=Clicker.on_delete_video,
                when="media_count",
            ),
            kbd.Button(
                Format("Добавить описание ✅"),
                id="confirm",
                when="media_count",
                on_click=kbd.Next(),
            ),
            kbd.Cancel(text=Const("Отменить"), when="media_count"),
        ),
        input.MessageInput(
            content_types=[ContentType.VIDEO], 
            func=on_input_videos_handler
        ),
        getter=Getter.get_media_group_videos,
        state=NewTrainingDialog.videos,
    ),
    Window(
        text.Const(
            "Введите описание тренировки 💪\n\n"
            "(максимальный размер текста 1024 символа)"
        ),
        input.TextInput(
            id='text_training_1', 
            on_success=on_input_text_handler
        ),
        kbd.Back(text=Const("Назад")),
        kbd.Cancel(text=Const("Отменить")),
        state=NewTrainingDialog.text,
    ),
    Window(
        Format(
            "Проверьте описание тринировок. 👇\n\n"
            "{text_training_1}\n\n"
            "Формат отображения будет без кнопок <b>Назад</b> и <b>Отменить</b>.\n"
            "Нажмите ✅, чтобы закончить создание тренировки!"
        ),
        kbd.Button(
            text=Const("✅"), 
            id="add", 
            on_click=Clicker.on_confirm_preview
        ),
        kbd.Back(text=Const("Назад")),
        kbd.Cancel(text=Const("Отменить")),
        state=NewTrainingDialog.view,
        getter=Getter.get_text_training
    ),
    Window(
        Const(
            "Тренировка успешно сохранена ✅\n"
            "Отправить рассылку?"
        ),
        kbd.Column(
            kbd.Row(
                kbd.Button(
                    Const("Да"),
                    id='yes_send_free', 
                    on_click=on_mailling_message
                ),
                kbd.Cancel(
                    Const("Нет"), 
                    id='not_send_free', 
                )
            ),
        ),
        state=NewTrainingDialog.send_free
    )
)