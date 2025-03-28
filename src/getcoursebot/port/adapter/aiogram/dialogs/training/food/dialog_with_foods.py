from decimal import Decimal
from aiogram import F, Bot, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.application.commands import CalculateDayNormCommand, InputeDayNormCommand
from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.domain.model.day_menu import TypeMeal
from getcoursebot.domain.model.proportions import СoefficientActivity
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import PaidStartingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import DayMenuDialog, FoodDialog, InputDialog



async def on_click_day_meny(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        DayMenuDialog.start,
        data={
            "type_meal": [
                TypeMeal.BREAKFAST,
                TypeMeal.LUNCH,
                TypeMeal.DINNER,
                TypeMeal.SNACK
            ],
            "user_id": callback.from_user.id,
            "recipes": {},
            "dirty_photos": [],
            "norma_kkal": dialog_manager.dialog_data["norma_kkal"]
        },
        show_mode=ShowMode.DELETE_AND_SEND
    )


@inject
async def get_user_data_for_kkal(
    dialog_manager: DialogManager,
    service: FromDishka[QueryService],
    **kwargs
):
    data_kkal = await service.query_exists_user_data_for_kkal(
        dialog_manager.start_data["user_id"]
    )
    dialog_manager.dialog_data["norma_kkal"] = data_kkal
    return data_kkal

    
food_dialog = Dialog(
    Window(
        text.Const(
            "У меня нет ваших данных КБЖУ.\n"
            "Хотите посчитать или ввести свои данные",
            when=~F["kkal"]
        ),
        text.Const(
            "Вот что можем сделать:",
            when=F["kkal"]
        ),
        kbd.Button(
            text.Const("Расчет КБЖУ"),
            id="cal_kbju",
            on_click=...
        ),
        kbd.Start(
            text.Const("Ввести КБЖУ"),
            id="input_kbju",
            state=InputDialog.start,
        ),
        kbd.Button(
            text.Const("Меню на день"),
            id="day_menu",
            when=F["kkal"],
            on_click=on_click_day_meny
        ),
        kbd.Start(
            text.Const("⬅️ На главную"),
            id="back_to_main_1",
            state=PaidStartingDialog.start,
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        ),
        state=FoodDialog.start,
        getter=get_user_data_for_kkal
    ),
)


async def get_data_activity(**kwargs):
    activity_types = [
        ("Минимальная", Decimal("1.2")),
        ("Слабая", Decimal("1.375")),
        ("Средняя", Decimal("1.55")),
        ("Высокая", Decimal("1.725")),
        ("Не знаю 😔", Decimal("1")),
    ]
    return {
        "c_types": activity_types,
        "count": len(activity_types)
    }


async def on_activity_selected(
    callback: t.CallbackQuery, 
    widget, 
    dialog_manager: DialogManager, 
    item_id
):
    dialog_manager.dialog_data["c_activity"] = Decimal(item_id)
    if item_id == СoefficientActivity.DEFAULT_A:
        bot: Bot = dialog_manager.middleware_data["bot"]
        await bot.send_voice(
            dialog_manager.start_data["user_id"],
            dialog_manager.start_data["voice_id"]
        )
    await dialog_manager.next()


async def on_target_selected(
    callback: t.CallbackQuery, 
    widget, 
    dialog_manager: DialogManager, 
    item_id,
    service: FromDishka[FitnessService] 
):
    dialog_manager.dialog_data["target"] = Decimal(item_id)
    await service.set_proportions(
        CalculateDayNormCommand(
            callback.from_user.id,
            Decimal(dialog_manager.find("inpute_age").get_value()),
            Decimal(dialog_manager.find("inpute_hieght").get_value()),
            Decimal(dialog_manager.find("inpute_weight").get_value()),
            dialog_manager.dialog_data["c_activity"],
            item_id
        )
    )
    await dialog_manager.next()

async def get_data_target(**kwargs):
    target_types = [
        ("Быстро похудеть", Decimal("-0.8")),
        ("Плавно похудеть", Decimal("-0.9")),
        ("Поддержание веса", Decimal("1")),
        ("Плавный набор", Decimal("1.1")),
        ("Быстрый набор", Decimal("1.2")),
    ]
    return {
        "types": target_types,
        "count": len(target_types)
    }


async def on_target_selected_input(
    callback: t.CallbackQuery, 
    widget, 
    dialog_manager: DialogManager, 
    item_id,
    service: FromDishka[FitnessService] 
):
    await service.set_input_user_data(
        InputeDayNormCommand(
            callback.from_user.id,
            Decimal(dialog_manager.find("inpute_kkal").get_value()),
            Decimal(dialog_manager.find("inpute_b").get_value()),
            Decimal(dialog_manager.find("inpute_j").get_value()),
            Decimal(dialog_manager.find("inpute_u").get_value()),
            dialog_manager.dialog_data["c_activity"],
            Decimal(item_id)
        )
    )
    await dialog_manager.next()


input_kbju_dialog = Dialog(
    Window(
        text.Const(
            "Напишите вашу дневную норму Калорий.\n"
            "Пришлите только цифры, например, 1650👇"
        ),
        input.TextInput(id="inpute_kkal", on_success=kbd.Next()),
        state=InputDialog.start
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму белков.\n"
            "Пришлите только цифры, например, 120👇"
        ),
        input.TextInput(id="inpute_b", on_success=kbd.Next()),
        state=InputDialog.b
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму жиров.\n"
            "Пришлите только цифры, например, 55👇"
        ),
        input.TextInput(id="inpute_j", on_success=kbd.Next()),
        state=InputDialog.j
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму углеводов.\n"
            "Пришлите только цифры, например, 220👇"
        ),
        input.TextInput(id="inpute_u", on_success=kbd.Next()),
        state=InputDialog.u
    ),
    Window(
        text.Const("Выберите Ваш уровень активности:"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="s_types",
                item_id_getter=lambda x: x[1],
                items="c_types",
                on_click=on_activity_selected
            )
        ),
        state=InputDialog.activity,
        getter=get_data_activity
    ),
    Window(
        text.Const("Выберите цель меню:"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="s_2_types",
                item_id_getter=lambda x: x[1],
                items="types",
                on_click=on_target_selected_input
            )
        ),
        state=InputDialog.target,
        getter=get_data_target
    ),
    # Window(
    #     text.Format(
    #         "Итак, необходимо ежедневно:\n\n"
    #         "ККал - {kkal}\n"
    #         "Белки - {b}\n"
    #         "Жиры - {j}\n"
    #         "Углеводы - {u}\n\n"
    #         "Дальше я буду подбирать вам рецепты ежедневно, чтобы уложиться в эти цифры."
    #         "Вы также можете ввести свои КБЖУ в первом разделе питания, "
    #         "если хотите, и я буду подбирать рецепты под них."
    #     ),
    #     kbd.Button(
    #         text.Const("Меню на день"), 
    #         id="day_menu_3", 
    #         on_click=Clicker.on_day_menu,
    #     ),
    #     kbd.Button(text.Const("⬅️ На главную"), id="in_main_3", on_click=Clicker.on_in_main_calc_hbju),
    #     state=InputDialog.end,
    #     getter=Getter.get_user_data
    # )
)