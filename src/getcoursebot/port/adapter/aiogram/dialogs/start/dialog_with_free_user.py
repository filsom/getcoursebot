import asyncio
from email_validator import validate_email, EmailNotValidError
from aiogram import F, Bot, types as t
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window, BaseDialogManager
from aiogram_dialog.widgets import kbd, text, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_states import PaidStartingDialog


class AnonUserDialog(StatesGroup):
    start = State()
    inputed_email = State()


class FreeUserDialog(StatesGroup):
    start = State()
    check_access = State()


async def send_start_training_handler(
    user_id: int,
    bg: BaseDialogManager,
    bot: Bot,
    service: QueryService,
    last_training: dict
):
    await asyncio.sleep(4)

    builder = MediaGroupBuilder()
    caption = False
    for media in last_training["media"]:
        if not caption:
            if len(last_training["text"]) < 1024:
                builder.add_video(media.file_id, caption=last_training["text"])
                caption = True
        builder.add_video(media.file_id)
    if caption:
        await bot.send_media_group(user_id, media=builder.build())
    else:
        await bot.send_media_group(user_id, media=builder.build())
        await bot.send_message(user_id, last_training["text"])

    await asyncio.sleep(4)
    await bg.start(
        FreeUserDialog.start,
        show_mode=ShowMode.DELETE_AND_SEND,
        mode=StartMode.RESET_STACK
    )

async def get_input_email(dialog_manager: DialogManager, **kwargs):
    return {"email": dialog_manager.find("email_input").get_value()}


@inject
async def input_email_handler(
    message: t.Message,
    button,
    dialog_manager: DialogManager,
    value,
    service: FromDishka[FitnessService],
    query_service: FromDishka[QueryService],
    **kw
):  
    try:
        email_info = validate_email(value)
        await service.create_free_user(
            message.from_user.id,
            email_info.normalized
        )
        last_training = await query_service.query_last_training()
        bot = dialog_manager.middleware_data["bot"]
        bg_manager = dialog_manager.bg(user_id=message.from_user.id)
        _ = asyncio.create_task(send_start_training_handler(
            message.from_user.id,
            bg_manager,
            bot,
            query_service,
            last_training
        ))
        await dialog_manager.next()
    except EmailNotValidError:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await message.answer("Некорректный @email адрес ❌")


anon_starting_dialog = Dialog(
    Window(
        text.Const("Здравствуйте. Пожалуйста, введите Ваш @email 👇🏻", when=~F["user_id"]),
        input.TextInput(id="email_input", on_success=input_email_handler),
        state=AnonUserDialog.start,
    ),
    Window(
        text.Format(
            "Приветсвую 👋🏻\n\nВаш @email - {email}\n"
            "Активирована бесплатная подписка.\n\nВам будут приходить новые тренировки в этот чат, когда Мила их будет записывать ❤️\n\nВот самая свежая 👇🏻",
            when=F["email"]
        ),
        getter=get_input_email,
        state=AnonUserDialog.inputed_email
    )
)


@staticmethod
@inject
async def on_click_im_paid(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    access_user = await service.query_user_roles(
        callback.from_user.id
    )
    if access_user.groups_empty():
        await dialog_manager.next()
    else:
        await dialog_manager.start(
            PaidStartingDialog.start,
            data={
                "user_id": callback.from_user.id,
                "roles": access_user.groups
            },
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        )


@staticmethod
@inject
async def on_click_check_access(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    access_user = await service.query_user_roles(
        callback.from_user.id
    )
    if access_user.groups_empty():
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await callback.message.answer("Вас нету ни в одной группе ❌")
        return 
    else:
        await dialog_manager.start(
            PaidStartingDialog.start,
            data={
                "user_id": callback.from_user.id,
                "roles": access_user.groups
            },
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        )


free_starting_dialog = Dialog(
    Window(
        text.Const(
            "Получите доступ ко всей базе 200+ тренировок\n"
            "и конструктору индивидуального меню,\n"
            "занимайтесь дома в удобное время и питайтесь правильно без подсчета калорий!\n\n"
            "Подробнее по ссылке https://workoutmila.ru/bot_payment"
        ),
        kbd.Column(
            kbd.Button(text.Const("Я оплатила"), id="im_paid", on_click=on_click_im_paid),
        ),
        state=FreeUserDialog.start,
    ),
    Window(
        text.Const(
            "Пока не вижу вашу оплату. Обычно данные обновляются в течение часа.\n"
            "Вы можете нажать кнопку ниже чуть позже, чтобы снова проверить подписку.\n"
            "Если доступ не появляется, напишите нам @Workout_mila_bot"
        ),
        kbd.Button(
            text.Const("Проверить доступ"),
            id="check_access",
            on_click=on_click_check_access
        ),
        state=FreeUserDialog.check_access,
    ),
)
