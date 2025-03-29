from datetime import datetime

from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram import Bot, types as t
from aiogram.enums import ContentType
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from aiogram_dialog.widgets import kbd
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from getcoursebot.application.commands import CreateUserCommand
from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.domain.model.user import IDRole, NameRole
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_states import (
    AddAccessDialog,
    CloseAccessDialog,
    FreeStartingDialog, 
    PaidStartingDialog, 
    TrySubDialog,
    UsersGroupsDialog
)
from getcoursebot.port.adapter.aiogram.dialogs.training.food.dialog_states import (
    DayMenuDialog,
    FoodDialog,
    NewTrainingDialog, 
    TrainingDialog
)


MAP = {
    IDRole.Food: NameRole.Food,
    IDRole.Admin: NameRole.Admin,
    IDRole.Training: NameRole.Training,
}


class Getter:
    @staticmethod
    async def get_input_categoty_name(
        dialog_manager: DialogManager,
        **kwargs,
    ):
        return {"category_name": dialog_manager.dialog_data["category_name"]}
    
    @staticmethod
    @inject
    async def get_paging_menu(
        service: FromDishka[QueryService],
        dialog_manager: DialogManager,
        **kwargs,
    ):
        current_page = await dialog_manager.find("stub_scroll_1").get_page()
        if dialog_manager.dialog_data.get("day_menu", None) is None:
            menu = await service.query_day_meny(
                dialog_manager.start_data["user_id"],
                datetime.now().date()
            )
            if menu is None:
                return {"menu": None}
            
            dialog_manager.dialog_data["day_menu"] = menu.repr()

        return {
            "menu": True,
            "pages": len(dialog_manager.dialog_data["day_menu"]),
            "current_page": current_page + 1,
            "title": dialog_manager.dialog_data["day_menu"][current_page]["title"],
            "photo": MediaAttachment(
                ContentType.PHOTO,
                file_id=MediaId(dialog_manager.dialog_data["day_menu"][current_page]["photo_id"])
            ),
            "ingredients": dialog_manager.dialog_data["day_menu"][current_page]["ingredients"],
            "text": dialog_manager.dialog_data["day_menu"][current_page]["text"],
        }

    @staticmethod
    async def get_new_sub_email(
        dialog_manager: DialogManager, 
        **kwargs,
    ):
        return {"new_sub_email": dialog_manager.dialog_data["new_sub_email"]}
    
    @staticmethod
    @inject
    async def get_email_and_roles(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService],
        **kwargs,
    ):
        data = await service.query_roles_with_id(
            dialog_manager.start_data["user_id"]
        )
        dialog_manager.dialog_data.update(**data)
        return data
    
    @staticmethod
    @inject
    async def get_user_sub_email_and_roles(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService],
        **kwargs,
    ):
        data = await service.query_roles_with_email(
            dialog_manager.dialog_data["sub_email"]
        )
        dialog_manager.dialog_data.update(**data)
        return data
    
    @staticmethod
    async def get_inputed_email(
        dialog_manager: DialogManager,
        **kwargs
    ):
        return {"email": dialog_manager.dialog_data["email"]}

    @staticmethod
    @inject
    async def get_user_roles(
        dialog_manager: DialogManager, 
        service: FromDishka[QueryService],
        **kwargs
    ):
        data = await service.query_roles_with_id(
            dialog_manager.start_data["user_id"]
        )
        return data
    
    @staticmethod
    @inject
    async def get_kbd_status(
        dialog_manager: DialogManager,
        **kwargs
    ):         
        return {
            "training": dialog_manager.dialog_data["training"],
            "food": dialog_manager.dialog_data["food"]
        }
    
    @staticmethod
    async def get_names_roles(
        dialog_manager: DialogManager, 
        **kwargs
    ):
        names_roles = []
        for role in [
            (NameRole.Food, IDRole.Food), 
            (NameRole.Training, IDRole.Training), 
            (NameRole.Admin, IDRole.Admin)
        ]:
            names_roles.append(role)

        return {
            "name_roles": names_roles,
            "count": len(names_roles)
        } 

    
class Clicker:
    NAMES_ROLES = {
        IDRole.Admin: NameRole.Admin,
        IDRole.Food: NameRole.Food,
        IDRole.Training: NameRole.Training,
        IDRole.Free: NameRole.Free
    }
    
    @staticmethod
    @inject
    async def on_add_new_сategory(
        callback: t.CallbackQuery,
        button: kbd.Select,
        dialog_manager: DialogManager,
        service: FromDishka[FitnessService],
    ):
        await service.add_new_category(
            callback.from_user.id,
            dialog_manager.dialog_data["category_name"]
        )
        await dialog_manager.done()

    @staticmethod
    @inject
    async def upload_from_exele(
        callback: t.CallbackQuery,
        button: kbd.Select,
        dialog_manager: DialogManager,
        service: FromDishka[FitnessService],
    ):
        await service.add_new_category(
            callback.from_user.id
        )

    @staticmethod
    @inject
    async def upload_from_exele(
        callback: t.CallbackQuery,
        button: kbd.Select,
        dialog_manager: DialogManager,
        service: FromDishka[FitnessService],
    ):
        await service.upload_recipe()


    @staticmethod
    @inject
    async def on_add_training(
        callback: t.CallbackQuery,
        button: kbd.Select,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService],
    ):
        await dialog_manager.start(
            NewTrainingDialog.start,
            show_mode=ShowMode.EDIT,
            mode=StartMode.NORMAL,
            data={"from_training": True}
        )

    @staticmethod
    async def on_users_groups(
        callback: t.CallbackQuery,
        button: kbd.Select,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService],
    ):
        await dialog_manager.start(
            AddAccessDialog.start,
        )

    @staticmethod
    @inject
    async def on_click_access(
        callback: t.CallbackQuery,
        button: kbd.Select,
        dialog_manager: DialogManager,
        item_id,
        service: FromDishka[QueryService],
    ):
        if Clicker.NAMES_ROLES.get(int(item_id)) in dialog_manager.start_data["roles"]:
            await dialog_manager.switch_to(
                state=AddAccessDialog.not_access,
                show_mode=ShowMode.EDIT
            )
        else:
            await service.insert_role(
                dialog_manager.start_data["sub_email"],
                int(item_id),
                MAP.get(int(item_id))
            )
            await dialog_manager.switch_to(
                state=AddAccessDialog.access,
                show_mode=ShowMode.EDIT
            )

    @staticmethod
    @inject
    async def on_click_close_access(
        callback: t.CallbackQuery,
        button: kbd.Select,
        dialog_manager: DialogManager,
        item_id,
        service: FromDishka[QueryService],
    ):
        if Clicker.NAMES_ROLES.get(int(item_id)) in dialog_manager.start_data["roles"]:
            await service.delete_role(
                dialog_manager.start_data["sub_email"],
                int(item_id)
            )
            await dialog_manager.switch_to(
                state=CloseAccessDialog.close_access,
                show_mode=ShowMode.EDIT
            )
        else:
            await dialog_manager.switch_to(
                state=CloseAccessDialog.not_close_access,
                show_mode=ShowMode.EDIT
            )

    @staticmethod
    @inject
    async def on_training(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService]
    ):
        data = await service.query_roles_with_id(
            callback.from_user.id
        )
        if NameRole.Training not in data["roles"]:
            dialog_manager.dialog_data["training"] = False
            dialog_manager.dialog_data["food"] = True
            await dialog_manager.next()
        else:
            await dialog_manager.start(
                TrainingDialog.start,
                data={
                    "user_id": callback.from_user.id,
                    "roles": data["roles"],
                },
                mode=StartMode.NORMAL,
                show_mode=ShowMode.EDIT
            )

    @staticmethod
    @inject
    async def on_my_meny(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService]
    ):
        data = await service.query_day_menu_id(
            callback.from_user.id,
            str(datetime.now().date())
        )
        data1 = await service.query_roles_with_id(
            callback.from_user.id
        )
        # Добавить чтобы админ смог смотреть меню
        if NameRole.Food in data1["roles"]: 
            if data["menu_id"] is None:
                await dialog_manager.start(
                    DayMenuDialog.breakfast,
                    data={
                        "temporal_recipes": [],
                        "recipe": []
                    },
                    show_mode=ShowMode.EDIT,
                    mode=StartMode.RESET_STACK
                )
            else:
                await dialog_manager.start(
                    PaidStartingDialog.menu,
                    data={"user_id": callback.from_user.id}
                )
        else:
            dialog_manager.dialog_data["training"] = True
            dialog_manager.dialog_data["food"] = True
            await dialog_manager.next()

    @staticmethod
    @inject
    async def on_food(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService]
    ):
        data = await service.query_user_data(
            callback.from_user.id
        )
        if NameRole.Food in data["roles"] or NameRole.Admin in data["roles"]:
            await dialog_manager.start(
                FoodDialog.start,
                data={
                    "user_id": callback.from_user.id,
                    "roles": data["roles"],
                    "kkal": data["kkal"],
                },
                mode=StartMode.NORMAL,
                show_mode=ShowMode.EDIT
            )
        else:
            dialog_manager.dialog_data["training"] = True
            dialog_manager.dialog_data["food"] = False
            await dialog_manager.next()
            
    @staticmethod
    @inject
    async def on_confirmed_email(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[FitnessService]
    ):
        roles = await service.create_user(
            CreateUserCommand(
                callback.from_user.id, 
                dialog_manager.dialog_data["email"]
            )
        )
        await dialog_manager.start(
            FreeStartingDialog.start,
            data={
                "user_id": callback.from_user.id,
                "email": dialog_manager.dialog_data["email"],
                "roles": roles,
            },
            show_mode=ShowMode.EDIT
        )

    @staticmethod
    @inject
    async def on_paid(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
    ):
        await dialog_manager.start(
            TrySubDialog.start,
            data={
                "user_id": callback.from_user.id,
            },
            show_mode=ShowMode.DELETE_AND_SEND
        )

    @staticmethod
    @inject
    async def on_access(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService]
    ):
        data = await service.query_roles_with_id(
            dialog_manager.start_data["user_id"]
        )
        print(data)
        if NameRole.Free not in data["roles"]:
            await dialog_manager.start(
                PaidStartingDialog.start,
                data={
                    "user_id": callback.from_user.id,
                    "roles": data["roles"]
                },
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.EDIT
            )
        else:
            await dialog_manager.next()

    @staticmethod
    @inject
    async def on_view_video(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService]
    ):
        bot: Bot = dialog_manager.middleware_data["bot"]
        await service.update_on_view_status(callback.from_user.id, False)
        message = await bot.send_message(callback.from_user.id, "Здесь будет видео!")
        # Сохранить видео

    @staticmethod
    @inject
    async def on_add_access(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService]
    ):  
        if NameRole.Admin in dialog_manager.dialog_data["roles"]:
            await dialog_manager.start(
                state=AddAccessDialog.start,
                data={
                    "sub_user_id": dialog_manager.dialog_data["sub_user_id"],
                    "sub_email": dialog_manager.dialog_data["sub_email"],
                    "roles": dialog_manager.dialog_data["roles"]
                },
                show_mode=ShowMode.EDIT,
                mode=StartMode.NORMAL
            )

    @staticmethod
    @inject
    async def on_сlose_access(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
    ):  
        print(dialog_manager.dialog_data["roles"])
        if NameRole.Admin not in dialog_manager.dialog_data["roles"]:
            await dialog_manager.start(
                state=CloseAccessDialog.start,
                data={
                    "sub_user_id": dialog_manager.dialog_data["sub_user_id"],
                    "sub_email": dialog_manager.dialog_data["sub_email"],
                    "roles": dialog_manager.dialog_data["roles"]
                },
                show_mode=ShowMode.EDIT,
                mode=StartMode.NORMAL
            )

    @staticmethod
    @inject
    async def on_сlose_dialog(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
    ):  
        await dialog_manager.start(
            state=UsersGroupsDialog.start,
            data={
                "sub_user_id": dialog_manager.dialog_data["sub_user_id"],
                "sub_email": dialog_manager.dialog_data["sub_email"],
                "roles": dialog_manager.dialog_data["roles"]
            },
            show_mode=ShowMode.EDIT
        )

    @staticmethod
    @inject
    async def on_save_change_email(
        callback: t.CallbackQuery,
        button,
        dialog_manager: DialogManager,
        service: FromDishka[QueryService]
    ):  
        await service.update_user_email(
            dialog_manager.dialog_data["sub_email"],
            dialog_manager.dialog_data["new_sub_email"]
        )
        await dialog_manager.switch_to(
            UsersGroupsDialog.profile,
            show_mode=ShowMode.EDIT
        )
        dialog_manager.dialog_data["sub_email"] = dialog_manager.dialog_data["new_sub_email"]
        

async def email_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
):
    await message.delete()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    dialog_manager.dialog_data["sub_email"] = message.text.lower()
    await dialog_manager.next()

async def inpute_email_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
):
    await message.delete()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    dialog_manager.dialog_data["email"] = message.text.lower()
    await dialog_manager.next()


async def inpute_name_category_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
    _
):
    await message.delete()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    dialog_manager.dialog_data["category_name"] = message.text
    await dialog_manager.next()


async def change_email_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
):
    await message.delete()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    dialog_manager.dialog_data["new_sub_email"] = message.text.lower()
    await dialog_manager.next()


async def delete_message_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
):
    await message.delete()


async def process_result_handler(
    start_data,
    result,
    dialog_manager: DialogManager
):
    if result:
        dialog_manager.dialog_data["roles"] = result["roles"]
