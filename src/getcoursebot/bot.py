import asyncio

from typing import AsyncGenerator
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram_dialog import setup_dialogs

from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider, setup_dishka

from getcoursebot.port.adapter.dependency_provider import DependencyProvider
from getcoursebot.port.adapter.aiogram.dialogs.resources import starting_router
from getcoursebot.port.adapter.aiogram.dialogs.training.food import content_router
from getcoursebot.port.adapter.orm import mappers, metadata, mapper


mappers(mapper)
async def main():
    engine = create_async_engine(
        'postgresql+psycopg://postgres:som@localhost:5433',
        echo=False
    )
    bot = Bot("7682965504:AAEX7p2SPM_Kq8ZRsg-1L9nuNnqATvL6h_I", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage, events_isolation=SimpleEventIsolation())
    dp.include_router(starting_router)
    dp.include_router(content_router)

    container = make_async_container(
        DependencyProvider(),
        AiogramProvider(),
        context={AsyncGenerator[AsyncEngine, None]: engine}
    )
    setup_dishka(container=container, router=dp)
    setup_dialogs(dp)

    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
        await connection.commit()

    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())