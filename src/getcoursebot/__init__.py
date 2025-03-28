# import asyncio
# import logging
# import os

# from aiogram import Bot, Dispatcher
# from aiogram.filters import CommandStart
# from aiogram.filters.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import Message
# from dishka.integrations.aiogram_dialog import inject
# from dishka import FromDishka
# from aiogram_dialog import (
#     Dialog,
#     DialogManager,
#     LaunchMode,
#     StartMode,
#     Window,
#     setup_dialogs,
# )
# from aiogram_dialog.widgets.kbd import Cancel, Row, Start
# from aiogram_dialog.widgets.text import Const, Format

# from getcoursebot.port.adapter.query_service import QueryService

# API_TOKEN = os.getenv("BOT_TOKEN")


# class BannerSG(StatesGroup):
#     default = State()


# class MainSG(StatesGroup):
#     default = State()


# class Product(StatesGroup):
#     show = State()


# banner = Dialog(
#     Window(
#         Const("BANNER IS HERE"),
#         Start(Const("Try start"), id="start", state=MainSG.default),
#         Cancel(),
#         state=BannerSG.default,
#     ),
#     launch_mode=LaunchMode.EXCLUSIVE,
# )
# main_menu = Dialog(
#     Window(
#         Const("This is main menu"),
#         Start(Const("Product"), id="product", state=Product.show),
#         Cancel(),
#         state=MainSG.default,
#     ),
#     # we do not worry about resetting stack
#     # each time we start dialog with ROOT launch mode
#     launch_mode=LaunchMode.ROOT,
# )

# @inject
# async def product_getter(dialog_manager: DialogManager, query: FromDishka[QueryService], **kwargs):
#     res = await query.query_training()
#     return {
#         "data": dialog_manager.current_context().id,
#     }


# product = Dialog(
#     Window(
#         Const("Выберите категорию"),
#         kbd.Column(
#             kbd.Select(
#                 id='id_type_training',
#                 text=Format("{item[0]}"),
#                 items="type_categories",
#                 item_id_getter=operator.itemgetter(1),
#                 on_click=on_click_type_category_2
#             ),
#         ),
#         state=UserTrainingSG.category,
#         getter=[get_types_training]
#     ),
#     Window(
#         Format("This is product: {data}"),
#         Row(
#             Start(Const("Main menu"), id="main", state=MainSG.default),
#             Start(Const("Banner"), id="banner", state=BannerSG.default),
#             Start(Const("Product"), id="product", state=Product.show),
#         ),
#         Cancel(),
#         getter=product_getter,
#         state=Product.show,
#     ),
#     # when this dialog is on top and tries to launch a copy
#     # it just replaces himself with it
#     launch_mode=LaunchMode.SINGLE_TOP,
# )


# async def start(message: Message, dialog_manager: DialogManager):
#     # it is important to reset stack because user wants to restart everything
#     await dialog_manager.start(MainSG.default, mode=StartMode.RESET_STACK)


# async def main():
#     # real main
#     logging.basicConfig(level=logging.INFO)
#     storage = MemoryStorage()
#     bot = Bot("7876069205:AAHPIqlXJjp5KOGF25_MGJY5YohgRh1oOac")
#     dp = Dispatcher(storage=storage)
#     dp.include_routers(banner, product, main_menu)

#     dp.message.register(start, CommandStart())
#     setup_dialogs(dp)
#     await dp.start_polling(bot)


# if __name__ == "__main__":
#     asyncio.run(main())