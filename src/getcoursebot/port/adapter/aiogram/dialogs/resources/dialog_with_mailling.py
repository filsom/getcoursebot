import asyncio
import operator
import re
from uuid import uuid4
from aiogram import F, Bot, types as t
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window, BaseDialogManager
from aiogram_dialog.widgets import text, kbd, input, media, common
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from dishka.integrations.aiogram_dialog import inject
from dishka import FromDishka
from aiogram.utils.media_group import MediaGroupBuilder

from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.domain.model.training import MaillingMedia, Malling, Media, Photos
from getcoursebot.domain.model.user import IDRole, NameRole
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import AdminStartingDialog


class MaillingDialog(StatesGroup):
    start = State()
    new_mall = State()
    inpute_photo = State()
    text = State()
    send_admin = State()
    send_status = State()
    data_input = State()
    access = State()


class SendDialog(StatesGroup):
    start = State()


class PlandeMaillingDialog(StatesGroup):
    start = State()


async def get_data_users_roles(**kwargs):
    roles = [
        ("платным", "paid"),
        ("бесплатным", "free")
    ]
    return {
        "roles": roles
    }


async def on_input_photo(
    message: t.Message,
    widget: input.MessageInput,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data.setdefault("photos", []).append(
        (message.photo[-1].file_id, message.photo[-1].file_unique_id, message.message_id, message.content_type),
    )


async def on_delete(
        callback: t.CallbackQuery, widget: kbd.Button, dialog_manager: DialogManager,
):
    scroll: common.ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    del photos[media_number]
    if media_number > 0:
        await scroll.set_page(media_number - 1)


async def on_delete(
        callback: t.CallbackQuery, widget: kbd.Button, dialog_manager: DialogManager,
):
    scroll: common.ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    del photos[media_number]
    if media_number > 0:
        await scroll.set_page(media_number - 1)


async def on_role_selected(
    callback: t.CallbackQuery, 
    widget,
    dialog_manager: DialogManager, 
    item_id: str   
):
    text = dialog_manager.start_data.get("text_mailling_mess", None)
    media = dialog_manager.start_data.get("photos", None)
    if text is not None:
        dialog_manager.dialog_data["text_mailling_mess"] = text
    if media is not None:
        dialog_manager.dialog_data["photos"] = media
    if item_id == "free":
        dialog_manager.dialog_data["roles"] = [IDRole.Free]
    else:
        dialog_manager.dialog_data["roles"] = [IDRole.Food, IDRole.Training]

    await dialog_manager.next()


async def getter(dialog_manager: DialogManager, **kwargs) -> dict:
    scroll: common.ManagedScroll = dialog_manager.find("pages")
    media_number = await scroll.get_page()
    photos = dialog_manager.dialog_data.get("photos", [])
    if photos:
        x = []
        for i in photos:
            x.append((i[0], i[1]))
        photo = x[media_number]
        media = MediaAttachment(
            file_id=MediaId(*photo),
            type=ContentType.PHOTO,
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


async def on_input_text_handler_mailling(
    message: t.Message, 
    source, 
    dialog_manager: DialogManager, 
    _
):
    await message.delete()
    dialog_manager.show_mode = ShowMode.EDIT
    dialog_manager.dialog_data["text_mailling_mess"] = message.html_text
    await dialog_manager.next()


async def get_text_mailling(
    dialog_manager: DialogManager, 
    **kwargs
):
    return {"text_mailling_1": dialog_manager.dialog_data["text_mailling_mess"]}



@inject
async def getter_1(
    dialog_manager: DialogManager, 
    service: FromDishka[QueryService],
    **kwargs
) -> dict:
    data = await service.query_mailling()
    return data


@inject
async def on_click_planed_mailling(
    callback: t.CallbackQuery, widget: kbd.Button, dialog_manager: DialogManager, item_id, service: FromDishka[QueryService]
):
    malling = await service.get_malling_and_delete(item_id)
    x = malling.text
    ppp = [(f.file_id, f.file_uniq_id, f.message_id, f.content_type) for f in malling.photos]
    i = malling.mailling_id
    users = await service.query_users_all_with_role(malling.mailling_roles)
    bot = dialog_manager.middleware_data["bot"]
    _ = asyncio.create_task(send_message_photo(users, x, ppp, bot))
    await dialog_manager.done()
    await service.delete_malling(i)


planed_mailling_dialog = Dialog(
    Window(
        text.Const("Нажмите, чтобы разослать."),
        kbd.Column(kbd.Select(
            text.Format("По {item[0]} от {item[1]}"),
            id="s_planed_mailling",
            item_id_getter=operator.itemgetter(2),
            items="planed",
            on_click=on_click_planed_mailling,
        )),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_planed_mailling",
        ),
        getter=getter_1,
        state=PlandeMaillingDialog.start
    )
)


def is_valid_date_format(date_str):
    """
    Проверяет, соответствует ли строка формату DD-MM-YYYY.
    """
    pattern = r"^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$"
    return bool(re.match(pattern, date_str))


@inject
async def on_input_date_handler_mailling(
    message: t.Message, 
    source, 
    dialog_manager: DialogManager, 
    _,
    service: FromDishka[FitnessService]
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await message.delete()
    if not is_valid_date_format(message.text):
        await message.answer("Некорректная дата")
    else:
        x = []
        for i in dialog_manager.dialog_data["photos"]:
            x.append(MaillingMedia(i[2], i[0], i[1], i[3]))
        mailling = Malling(
            uuid4(),
            dialog_manager.dialog_data["roles"],
            dialog_manager.dialog_data["text_mailling_mess"],
            message.text,
            x
        )
        await service.add_mailling(mailling)
    await dialog_manager.next()


async def on_message_admin_mailling(
    callback: t.CallbackQuery, widget: kbd.Button, dialog_manager: DialogManager,
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    bot: Bot = dialog_manager.middleware_data["bot"]
    builder = MediaGroupBuilder()
    # for video in sorted(data["training"].videos, key=lambda x: x.message_id):
    #     builder.add_video(video.file_id)
    if len(dialog_manager.dialog_data["photos"]) == 1:
        if len(dialog_manager.dialog_data["text_mailling_mess"]) < 1024:
            if dialog_manager.dialog_data["photos"][0][3] == 'photo':
                await bot.send_photo(
                    callback.from_user.id, 
                    dialog_manager.dialog_data["photos"][0][0],
                    caption=dialog_manager.dialog_data["text_mailling_mess"]
                )
            else:
                await bot.send_video(
                    callback.from_user.id, 
                    dialog_manager.dialog_data["photos"][0][0],
                    caption=dialog_manager.dialog_data["text_mailling_mess"]
                )
        else:
            if dialog_manager.dialog_data["photos"][0][3] == 'photo':
                await bot.send_photo(
                    callback.from_user.id, 
                    dialog_manager.dialog_data["photos"][0][0],
                    caption=dialog_manager.dialog_data["text_mailling_mess"]
                )
                await bot.send_message(
                    callback.from_user.id,
                    dialog_manager.dialog_data["text_mailling_mess"]
                )
            else:
                await bot.send_video(
                    callback.from_user.id, 
                    dialog_manager.dialog_data["photos"][0][0],
                )
                await bot.send_message(
                    callback.from_user.id,
                    dialog_manager.dialog_data["text_mailling_mess"]
                )
    else:
        builder = MediaGroupBuilder()
        capt = False
        for photo in dialog_manager.dialog_data["photos"]:
            if not capt:
                if len(dialog_manager.dialog_data["text_mailling_mess"]) < 1024:
                    builder.add(
                        type=photo[3],
                        media=photo[0],
                        caption=dialog_manager.dialog_data["text_mailling_mess"]
                    )
                    capt=True
            builder.add(type=photo[3], media=photo[0])
        if capt:
            await bot.send_media_group(callback.from_user.id, media=builder.build())
        else:
            await bot.send_media_group(callback.from_user.id, media=builder.build())
            await bot.send_message(
                callback.from_user.id,
                dialog_manager.dialog_data["text_mailling_mess"]
            )


class BG(StatesGroup):
    start = State()


bg_dialog = Dialog(
    Window(
        text.Const("Ehf"),
        state=BG.start
    )
)


@inject
async def on_click_send_mailling_for_users(
    callback: t.CallbackQuery, widget: kbd.Button, dialog_manager: DialogManager, service: FromDishka[QueryService]
):
    bot: Bot = dialog_manager.middleware_data["bot"]    
    text = dialog_manager.dialog_data["text_mailling_mess"]
    roles = dialog_manager.dialog_data["roles"]
    users = await service.query_users_all_with_role(
        roles
    )
    print(users, 'ffffffffff')
    _ = asyncio.create_task(send_message_photo(users, text, dialog_manager.dialog_data["photos"], bot))
    await dialog_manager.start(
        AdminStartingDialog.start,
        mode=StartMode.RESET_STACK
    )


async def send_message_photo(users, text, photos, bot: Bot):
    for user_id in users:
        try:
            if len(photos) == 1:
                if len(text) < 1024:
                    if photos[0][3] == 'photo':
                        await bot.send_photo(
                            user_id, 
                            photos[0][0],
                            caption=text
                        )
                    else:
                        await bot.send_video(
                            user_id, 
                            photos[0][0],
                            caption=text
                        )
                else:
                    if photos[0][3] == 'photo':
                        await bot.send_photo(
                            user_id, 
                            photos[0][0],
                        )
                        await bot.send_message(
                            user_id,
                            text
                        )
                    else:
                        await bot.send_video(
                            user_id, 
                            photos[0][0],
                        )
                        await bot.send_message(
                            user_id,
                            text
                        )
            else:
                builder = MediaGroupBuilder()
                capt = False
                for photo in photos:
                    if not capt:
                        if len(text) < 1024:
                            print('1')
                            builder.add(
                                type=photo[3],
                                media=photo[0],
                                caption=text
                            )
                            capt=True
                        else:
                            builder.add(
                                type=photo[3],
                                media=photo[0],
                            )
                if capt:
                    await bot.send_media_group(user_id, media=builder.build())
                else:
                    await bot.send_media_group(user_id, media=builder.build())
                    await bot.send_message(
                        user_id,
                        text
                    )
            await asyncio.sleep(0.33)       
        except Exception as e:
            raise e
            # continue


mailling_dialog = Dialog(
    Window(
        text.Const("Меню рассылки."),
        kbd.Button(text.Const("Новая рассылка +"), id="new_mallll", on_click=kbd.Next()),
        kbd.Start(
            text.Const("Запланированные"),
            id="planed_mailling",
            state=PlandeMaillingDialog.start,
            show_mode=ShowMode.EDIT,
        ),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_mailling",
        ),
        state=MaillingDialog.start
    ),
    Window(
        text.Format(
            "Отправьте фото для рассылки\n\n"
            "При отправке фото группой <b>не</b> <b>добавляйте</b> описание к ним,\n"
            "описание, будет добавлено на соответствующем шаге❗️",
            when=F["media_count"] == 0
        ),
        media.DynamicMedia(selector="media"),
        kbd.StubScroll(id="pages", pages="media_count"),
        kbd.Group(
            kbd.NumberedPager(
                scroll="pages", 
                when=F["pages"] > 1, 
                page_text=text.Format("№{target_page1}"), 
                current_page_text=text.Format("🔎")), 
                width=8
            ),
        kbd.Column(
            kbd.Button(
                text.Format("Удалить фото №{media_number} 🗑️"),
                id="del_photo",
                on_click=on_delete,
                when="media_count",
            ),
            kbd.Button(
                text.Format("Добавить описание ✅"),
                id="confirm_photo",
                when="media_count",
                on_click=kbd.Next(),
            ),
            kbd.Cancel(text=text.Const("⬅️ В Админ панель"), when="media_count"),
        ),
        input.MessageInput(
            content_types=[ContentType.PHOTO], 
            func=on_input_photo
        ),
        getter=getter,
        state=MaillingDialog.inpute_photo,
    ),
    Window(
        text.Const("Добавьте текст к рассылке."),
        input.TextInput(
            id='text_mailling_1', 
            on_success=on_input_text_handler_mailling
        ),
        kbd.Cancel(text=text.Const("⬅️ В Админ панель")),
        state=MaillingDialog.text,
    ),
    Window(
        text.Const("Выберите кому отправить."),
        kbd.Select(
            text.Format("Рассылка по {item[0]}"),
            id="s_roles",
            item_id_getter=operator.itemgetter(1),
            items="roles",
            on_click=on_role_selected,
        ),
        getter=get_data_users_roles,
        state=MaillingDialog.new_mall
    ),
    Window(
        text.Const("Прислать для просмотра?"),
        kbd.Button(
            text.Const("Прислать в ЛС"),
            id='text_mailling_228', 
            on_click=on_message_admin_mailling
        ),
        kbd.Button(text.Const("Подтвредить"), id="confirmed_mailling_123", on_click=kbd.Next()),
        kbd.Cancel(text=text.Const("⬅️ В Админ панель")),
        state=MaillingDialog.send_admin,
    ),
    Window(
        text.Const("Когда разослать?"),
        kbd.Button(
            text.Format("Сейчас"),
            id="send_try",
            on_click=on_click_send_mailling_for_users,
        ),
        kbd.Button(
            text.Format("Запланировать"),
            id="plan_send",
            on_click=kbd.Next(),
        ),
        kbd.Cancel(text=text.Const("⬅️ В Админ панель")),
        state=MaillingDialog.send_status,
    ),
    Window(
        text.Const("Введите дату в формате 01-01-2025"),
        input.TextInput(
            id="date_for_mailling",
            on_success=on_input_date_handler_mailling
        ),
        kbd.Cancel(text=text.Const("⬅️ В Админ панель")),
        state=MaillingDialog.data_input,
    ),
    Window(
        text.Const("Рассылка успешно зарегистрирована"),
        kbd.Cancel(text=text.Const("⬅️ В Админ панель")),
        state=MaillingDialog.access,
    ),
)