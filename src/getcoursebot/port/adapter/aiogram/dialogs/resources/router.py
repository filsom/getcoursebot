from aiogram import Router, types as t
from aiogram import filters as f
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka.integrations.aiogram import FromDishka, inject

from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_with_free_user import AnonUserDialog, FreeUserDialog
from getcoursebot.port.adapter.aiogram.dialogs.resources.dialog_with_paid_user import (
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
        if access_user.user_id is None:
            await dialog_manager.start(
                AnonUserDialog.start,
                mode=StartMode.RESET_STACK
            )
        else:
            await dialog_manager.start(
                FreeUserDialog.start,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.EDIT
            )
    # elif access_user.check_group(Group.ADMIN):
    #     await dialog_manager.start()
    
    else:
        await dialog_manager.start(
            state=PaidStartingDialog.start,
            data={"groups": access_user.groups},
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        )
    