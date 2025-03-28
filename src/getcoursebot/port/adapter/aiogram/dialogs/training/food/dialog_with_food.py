from datetime import datetime
from decimal import Decimal
import operator

from aiogram import F, Bot, types as t
from aiogram_dialog import Dialog, DialogManager, LaunchMode, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, input, kbd
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from getcoursebot.application.commands import CalculateDayNormCommand, InputeDayNormCommand
from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.domain.model.proportions import СoefficientActivity
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import PaidStartingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import CalculateDialog, DayMenuDialog, FoodDialog, InputDialog, WithDataDialog


class Getter:
    @staticmethod
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

    @staticmethod
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
    
    @staticmethod
    @inject
    async def get_user_data(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService], 
        **kwargs
    ):
        data = await service.query_users(
            dialog_manager.start_data["user_id"]
        )
        dialog_manager.dialog_data.update(**data)
        return dialog_manager.dialog_data
    
    @staticmethod
    @inject
    async def get_user_start_data(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService], 
        **kwargs
    ):
        data = await service.query_users(
            dialog_manager.start_data["user_id"]
        )
        dialog_manager.dialog_data.update(**data)
        return data


class Clicker:
    @staticmethod
    async def on_in_main_calc_hbju(
        callback: t.CallbackQuery, 
        widget, 
        dialog_manager: DialogManager, 
    ):
        dialog_manager.find()
        await dialog_manager.start(
            FoodDialog.start,
            data={
                "user_id": dialog_manager.dialog_data["user_id"],
                "kkal": dialog_manager.dialog_data["kkal"]
            },
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        )

    @staticmethod
    @inject
    async def on_day_menu(
        callback: t.CallbackQuery, 
        widget, 
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService]
    ):
        data = await service.query_day_menu_id(
            callback.from_user.id,
            datetime.now().date()
        )
        if data is None:
            await dialog_manager.start(
                DayMenuDialog.breakfast,
                data={
                    "temporal_recipes": [],
                    "recipe": []
                },
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.EDIT
            )
        else:
            await dialog_manager.start(
                PaidStartingDialog.start,
                data={
                    "user_id": callback.from_user.id,
                    "temporal_recipes": [],
                    "recipe": []
                },
            )
        
    @staticmethod
    @inject
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

    @staticmethod
    @inject
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
    
    @staticmethod
    async def on_calc_kbju(
        callback: t.CallbackQuery, 
        widget, 
        dialog_manager: DialogManager, 
    ):
        await dialog_manager.start(
            CalculateDialog.start, 
            {"user_id": callback.from_user.id},
            StartMode.RESET_STACK
        )

    @staticmethod
    async def on_input_kbju(
        callback: t.CallbackQuery, 
        widget, 
        dialog_manager: DialogManager, 
    ):
        await dialog_manager.start(
            InputDialog.start, 
            {"user_id": callback.from_user.id},
            StartMode.RESET_STACK
        )

    @staticmethod
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

    @staticmethod
    async def on_closed_dialog(
        callback: t.CallbackQuery, 
        widget, 
        dialog_manager: DialogManager, 
    ):
        await dialog_manager.done()
        builder = InlineKeyboardBuilder()
        builder.add(t.InlineKeyboardButton(text='Кушать', callback_data="food"))
        builder.add(t.InlineKeyboardButton(text='Тренироваться', callback_data="training"))
        await callback.message.edit_text(text="Что будем делать?", reply_markup=builder.as_markup())


# with_data_dialog = Dialog(
#     Window(
#         text.Format("{text}"),
#         kbd.Column(
#             kbd.Button(
#                 text.Const("Расчет КБЖУ"), 
#                 id="calc_kbju", 
#                 on_click=Clicker.on_calc_kbju
#             ),
#             kbd.Button(
#                 text.Const("Ввести КБЖУ"), 
#                 id="input_kbju",
#                 on_click=Clicker.on_input_kbju
#             ),
#             kbd.Cancel(text.Const("⬅️ На главную"), id="in_main", on_click=Clicker.on_closed_dialog)
#         ),
#         state=WithDataDialog.start,
#         getter=Getter.get_user_data
#     )
# )


class Inputter:
    pass


calculate_kbju_dialog = Dialog(
    Window(
        text.Const(
            "Напишите ваш текущий вес в кг.\n"
            "Пришлите только цифры, например, 72👇"
        ),
        input.TextInput(id="inpute_weight", on_success=kbd.Next()),
        state=CalculateDialog.start
    ),
    Window(
        text.Const(
            "Введите ваш рост в см.\n"
            "Пришлите только цифры, например, 165👇"
        ),
        input.TextInput(id="inpute_hieght", on_success=kbd.Next()),
        state=CalculateDialog.hieght
    ),
    Window(
        text.Const(
            "Напишите ваш возраст (лет).\n"
            "Пришлите только цифры, например, 35👇"
        ),
        input.TextInput(id="inpute_age", on_success=kbd.Next()),
        state=CalculateDialog.age
    ),
    Window(
        text.Const("Выберите Ваш уровень активности:"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="s_types",
                item_id_getter=lambda x: x[1],
                items="c_types",
                on_click=Clicker.on_activity_selected
            )
        ),
        state=CalculateDialog.activity,
        getter=Getter.get_data_activity
    ),
    Window(
        text.Const("Выберите цель меню:"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="s_1_types",
                item_id_getter=lambda x: x[1],
                items="types",
                on_click=Clicker.on_target_selected
            )
        ),
        state=CalculateDialog.target,
        getter=Getter.get_data_target
    ),
    Window(
        text.Format(
            "Вам необходимо ежедневно:\n\n"
            "ККал - {kkal}\n"
            "Белки - {b}\n"
            "Жиры - {j}\n"
            "Углеводы - {u}\n\n"
            "Дальше я буду подбирать вам рецепты ежедневно, чтобы уложиться в эти цифры."
            "Вы также можете ввести свои КБЖУ в первом разделе питания, "
            "если хотите, и я буду подбирать рецепты под них."
        ),
        kbd.Button(
            text.Const("Меню на день"), 
            id="day_menu_1", 
            on_click=Clicker.on_day_menu,
        ),
        kbd.Button(text.Const("⬅️ На главную"), id="in_main_1", on_click=Clicker.on_in_main_calc_hbju),
        state=CalculateDialog.end,
        getter=Getter.get_user_data
    )
)


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
            on_click=Clicker.on_calc_kbju
        ),
        kbd.Button(
            text.Const("Ввести КБЖУ"),
            id="inpute_kbju",
            on_click=Clicker.on_input_kbju
        ),
        kbd.Button(
            text.Const("Меню на день"),
            id="day_menu",
            when=F["kkal"],
            on_click=Clicker.on_day_menu
        ),
        kbd.Start(
            text.Const("⬅️ На главную"),
            id="main_start_1",
            state=PaidStartingDialog.start,
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        ),
        state=FoodDialog.start,
        getter=Getter.get_user_start_data
    ),
)


input_kbju_dialog = Dialog(
    Window(
        text.Const(
            "Напишите вашу дневную норму Калорий.\nПришлите только цифры, например, 1650👇"
        ),
        input.TextInput(id="inpute_kkal", on_success=kbd.Next()),
        state=InputDialog.start
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму белков.\nПришлите только цифры, например, 120👇"
        ),
        input.TextInput(id="inpute_b", on_success=kbd.Next()),
        state=InputDialog.b
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму жиров.\nПришлите только цифры, например, 55👇"
        ),
        input.TextInput(id="inpute_j", on_success=kbd.Next()),
        state=InputDialog.j
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму углеводов.\nПришлите только цифры, например, 220👇"
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
                on_click=Clicker.on_activity_selected
            )
        ),
        state=InputDialog.activity,
        getter=Getter.get_data_activity
    ),
    Window(
        text.Const("Выберите цель меню:"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="s_2_types",
                item_id_getter=lambda x: x[1],
                items="types",
                on_click=Clicker.on_target_selected_input
            )
        ),
        state=InputDialog.target,
        getter=Getter.get_data_target
    ),
    Window(
        text.Format(
            "Итак, необходимо ежедневно:\n\n"
            "ККал - {kkal}\n"
            "Белки - {b}\n"
            "Жиры - {j}\n"
            "Углеводы - {u}\n\n"
            "Дальше я буду подбирать вам рецепты ежедневно, чтобы уложиться в эти цифры."
            "Вы также можете ввести свои КБЖУ в первом разделе питания, "
            "если хотите, и я буду подбирать рецепты под них."
        ),
        kbd.Button(
            text.Const("Меню на день"), 
            id="day_menu_3", 
            on_click=Clicker.on_day_menu,
        ),
        kbd.Button(text.Const("⬅️ На главную"), id="in_main_3", on_click=Clicker.on_in_main_calc_hbju),
        state=InputDialog.end,
        getter=Getter.get_user_data
    )
)