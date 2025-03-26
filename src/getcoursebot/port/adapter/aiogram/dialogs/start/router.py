from aiogram import F, Bot, Router, types as t
from aiogram import filters as f
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka.integrations.aiogram import FromDishka, inject

from getcoursebot.domain.model.access import Group
from getcoursebot.domain.model.user import NameRole
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_states import AdminStartingDialog
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_with_free import (
    FreeStartingDialog
)
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_with_free_user import AnonUserDialog
from getcoursebot.port.adapter.aiogram.dialogs.start.dialog_with_paid import (
    PaidStartingDialog
)


starting_router = Router()


@starting_router.message(f.CommandStart())
@inject
async def start(
    message: t.Message, 
    dialog_manager: DialogManager,
    service: FromDishka[QueryService]
):
    await message.delete()
    access_user = await service.query_user_roles(
        message.from_user.id
    )
    if access_user.groups_empty():
        await dialog_manager.start(
            AnonUserDialog.start,
            mode=StartMode.RESET_STACK
        )
    elif access_user.check_group(Group.ADMIN):
        pass
    
    else:
        pass

    # if NameRole.Admin in data["roles"]:
    #     await dialog_manager.start(
    #         AdminStartingDialog.start, 
    #         data={"user_id": message.from_user.id, "roles": data["roles"]},
    #         mode=StartMode.RESET_STACK,
    #         show_mode=ShowMode.EDIT
    #     )
    # elif NameRole.Food in data["roles"] or NameRole.Training in data["roles"]:
    #     await dialog_manager.start(
    #         PaidStartingDialog.start, 
    #         data={"user_id": message.from_user.id, "roles": data["roles"]},
    #         mode=StartMode.RESET_STACK,
    #         show_mode=ShowMode.EDIT
    #     )
    # else:
    #     await dialog_manager.start(
    #         FreeStartingDialog.start, 
    #         data={"user_id": message.from_user.id, "email": data["email"]},
    #         mode=StartMode.RESET_STACK,
    #         show_mode=ShowMode.EDIT
    #     )