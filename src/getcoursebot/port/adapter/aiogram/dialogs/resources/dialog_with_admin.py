import operator
from aiogram import F
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, input, kbd
from getcoursebot.domain.model.user import IDRole, NameRole
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_helpers import Clicker, Getter, change_email_handler, email_handler, inpute_name_category_handler
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import AddAccessDialog, AddCategoryDialog, AdminStartingDialog, CloseAccessDialog, ContentBotDialog, PaidStartingDialog, UsersGroupsDialog
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_with_mailings import MaillingDialog
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import NewTrainingDialog


# Window(
    #     kbd.Select(
    #         text.Format("{name_mailing[0]}"),
    #         id="s_name_mailing",
    #         item_id_getter=operator.itemgetter(1),
    #         items="mailings",
    #         on_click=on_click_name_mailing
    #     ),
    #     getter=get_data_mailings
    # )


admin_starting_dialog = Dialog(
    Window(
        text.Format("Приветсвую, 👋🏻\n\nПанель администратора."),
        kbd.Column(
            kbd.Start(
                text.Const("Юзеры/Группы"),
                id="users_groups",
                state=UsersGroupsDialog.start,
                show_mode=ShowMode.EDIT,
                mode=StartMode.NORMAL,
            ),
            kbd.Start(
                text.Const("Контент"),
                id="content",
                state=ContentBotDialog.start,
                show_mode=ShowMode.EDIT,
                mode=StartMode.NORMAL,
            ),
            kbd.Start(
                text.Const("Рассылка"),
                id="mailling",
                state=MaillingDialog.start,
                show_mode=ShowMode.EDIT,
                mode=StartMode.NORMAL,
                data={}
            ),
            kbd.Start(
                text.Const("Разделы"),
                id="razdels",
                state=PaidStartingDialog.start,
                show_mode=ShowMode.EDIT,
                mode=StartMode.NORMAL,
                data={"roles": [IDRole.Admin]}
            ),
        ),
        state=AdminStartingDialog.start
    )
)


content_bot_dialog = Dialog(
    Window(
        text.Const("Управление контентом бота ⭐️"),
        kbd.Column(
            kbd.Button(
                text.Const("Добавить тренировку"),
                id="add_training",
                on_click=Clicker.on_add_training,
            ),
            kbd.Start(
                text.Const("Добавить категорию"),
                id="add_category",
                state=AddCategoryDialog.start,
                show_mode=ShowMode.EDIT,
            ),
            kbd.Button(
                text.Const("Выгрузить с Exele"),
                id="upload",
                on_click=Clicker.upload_from_exele,
            ),
            kbd.Cancel(
                text.Const("⬅️ В Админ панель"),
                id="to_main",
            ),
        ),
        state=ContentBotDialog.start
    )
)


add_new_category_dialog = Dialog(
    Window(
        text.Const("Введите название категории"),
        input.TextInput(id="add_new_cat_1", on_success=inpute_name_category_handler),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main_2"),
        state=AddCategoryDialog.start
    ),
    Window(
        text.Format("Подвтеридте создание новой категории - {category_name}"),
        kbd.Button(text.Const("Подтвредить ✅"), id="confirmed_name", on_click=Clicker.on_add_new_сategory),
        kbd.Back(text.Const("Изменить название"), id="to_input"),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main_3"),
        getter=Getter.get_input_categoty_name,
        state=AddCategoryDialog.confirm
    )
)


users_groups_dialog = Dialog(
    Window(
        text.Const("Введите @e-mail пользователя 🔎"),
        input.MessageInput(email_handler),
        kbd.Cancel(text.Const("⬅️ На главную")),
        state=UsersGroupsDialog.start,
    ),
    Window(
        text.Const("Пользователь не найден!", when=~F["sub_user_id"]),
        text.Format(
            "👤 id {sub_user_id}\n"
            "📧 @e-mail: {sub_email}\n"
            "👥 GC групп: {roles}\n"
        ),
        kbd.Button(
            text.Const("Дать доступ"),
            id="add_access",
            on_click=Clicker.on_add_access,
            when=F["sub_user_id"]
        ),
        kbd.Button(
            text.Const("Закрыть доступ"),
            id="close_access",
            on_click=Clicker.on_сlose_access,
            when=F["sub_user_id"]
        ),
        kbd.Button(
            text.Const("Изменить @e-mail"),
            id="change_email_1",
            on_click=kbd.Next(),
            when=F["sub_user_id"]
        ),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main",
        ),
        state=UsersGroupsDialog.profile,
        getter=Getter.get_user_sub_email_and_roles
    ),
    Window(
        text.Const("Введите новый @e-mail пользователя 🔎"),
        input.MessageInput(change_email_handler),
        kbd.Cancel(text.Const("⬅️ На главную")),
        state=UsersGroupsDialog.inpute_email
    ),
    Window(
        text.Format("Проверьте правильность ввода @e-mail - {new_sub_email}"),
        kbd.Button(
            text.Const("Сохранить изменения"),
            id="save_change_email",
            on_click=Clicker.on_save_change_email
        ),
        kbd.Back(text.Const("Ввести заново")),
        state=UsersGroupsDialog.change_email,
        getter=Getter.get_new_sub_email
    ),
)


add_access_dialog = Dialog(
    Window(
        text.Const("Выберите уровень доступа ✅"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="roles",
                item_id_getter=operator.itemgetter(1),
                items="name_roles",
                on_click=Clicker.on_click_access
            ),
        ),
        kbd.Cancel(text.Const("⬅️ На главную")),
        state=AddAccessDialog.start,
        getter=Getter.get_names_roles
    ),
    Window(
        text.Format("Доступ открыт ✅"),
        kbd.SwitchTo(
            text.Const("⬅️ На главную"),
            id='in_main_1',
            state=AddAccessDialog.start
        ),
        state=AddAccessDialog.access,
    ),
    Window(
        text.Format("У пользователя есть данный доступ."),
        kbd.SwitchTo(
            text.Const("⬅️ На главную"),
            id='in_main',
            state=AddAccessDialog.start
        ),
        state=AddAccessDialog.not_access
    )
)


close_access_dialog = Dialog(
    Window(
        text.Const("Выберите уровень доступа ⛔️"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="roles",
                item_id_getter=operator.itemgetter(1),
                items="name_roles",
                on_click=Clicker.on_click_close_access
            ),
        ),
        kbd.Cancel(text.Const("⬅️ На главную")),
        state=CloseAccessDialog.start,
        getter=Getter.get_names_roles
    ),
    Window(
        text.Format("Доступ закрыт ⛔️"),
        kbd.SwitchTo(
            text.Const("⬅️ На главную"),
            id='in_main_2',
            state=CloseAccessDialog.start
        ),
        state=CloseAccessDialog.close_access,
    ),
    Window(
        text.Format("У пользователя нету данного доступа."),
        kbd.SwitchTo(
            text.Const("⬅️ На главную"),
            id='in_main_3',
            state=CloseAccessDialog.start
        ),
        state=CloseAccessDialog.not_close_access
    )
)