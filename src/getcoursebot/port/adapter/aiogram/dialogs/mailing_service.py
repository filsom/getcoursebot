import asyncio
from datetime import datetime
from functools import partial
from uuid import UUID

from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import ShowMode
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from getcoursebot.application.error import AlreadyProcessMailing
from getcoursebot.domain.model.training import Mailing, MailingMedia, RecipientMailing, StatusMailing

from getcoursebot.port.adapter.orm import mailing_table, mailing_medias_table, users_table, roles_table


async def send_mailing_message(
    users_ids: list[int],
    mailing_id: UUID,
    mailing_media: list[dict],
    mailing_text: str,
    kbd,
    bot: Bot,
    engine: AsyncEngine
):
    builder = MediaGroupBuilder()
    content_type = mailing_media[0][1]
    for media in mailing_media:
        builder.add(
           type=content_type,
           media=media[0]
        )
    media_messages = builder.build()
    try:
        if not users_ids:
            return 
        for user_id in users_ids:
            await bot.send_media_group(user_id, media_messages)
            await bot.send_message(user_id, mailing_text, reply_markup=kbd)
            await asyncio.sleep(0.5)
    except Exception as err:
        pass
    finally:
        async with AsyncSession(engine) as session:
            gateway = MailingGateway(session)
            await gateway.update_status_mailing(
                mailing_id, 
                StatusMailing.DONE
            )
            await session.commit()


class MailingGateway:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_name(self, name: str, mailing_id: UUID) -> None:
        stmt = (
            sa.update(mailing_table)
            .values(name=name)
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        await self.session.execute(stmt)

    async def count_with_status(self, status) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(mailing_table)
            .where(mailing_table.c.status == status)
        )
        result = await self.session.execute(stmt)
        count = result.scalar()
        if count is None:
            return 0
        else:
            return count
        
    async def query_mailing_with_id(self, mailing_id: UUID) -> dict:
        mailing_stmt = (
            sa.select(
                mailing_table.c.text,
                mailing_table.c.type_recipient.label("type_recipient")
            )
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        media_stmt = (
            sa.select(
                mailing_medias_table.c.file_id,
                mailing_medias_table.c.content_type
            )
            .where(mailing_medias_table.c.mailing_id == mailing_id)
        )
        mailing_rows = await self.session.execute(mailing_stmt)
        media_rows = await self.session.execute(media_stmt)
        list_media = []
        for media in media_rows:
            list_media.append((media[0], media[1]))
        for row in mailing_rows:
            text = row.text
            type_recipient = row.type_recipient
        return {
            "text": text,
            "type_recipient": type_recipient,
            "media": list_media
        }
    async def query_all_user_id_with_role(self, is_exists: bool = False) -> list[int]:
        stmt = sa.select(users_table.c.user_id).where()
        subq_stmt = sa.select(roles_table.c.email)
        if not is_exists:
            stmt = stmt.where(users_table.c.email.not_in(subq_stmt))
        else:
            stmt = stmt.where(users_table.c.email.in_(subq_stmt))

        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def update_status_mailing(self, mailing_id: UUID, status: StatusMailing) -> None:
        stmt = (
            sa.update(mailing_table)
            .values(status=status)
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        await self.session.execute(stmt)

    async def delete(self, mailing_id: UUID) -> None:
        stmt = (
            sa.delete(mailing_table)
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        await self.session.execute(stmt)


class TelegramMailingService:
    def __init__(
        self, 
        session: AsyncSession,
        gateway: MailingGateway
    ):
        self.session = session
        self.gateway = gateway

    async def add_new_mailing(
        self,
        mailing_id: UUID,
        name_mailing: str,
        text_mailing: str,
        rows_media: list[dict[str, str]],
        type_recipient: int,
        status: str
    ):
        async with self.session.begin():
            media = []
            for row in rows_media:
                media.append(MailingMedia(**row))
            
            new_mailing = Mailing(
                mailing_id,
                name_mailing,
                text_mailing,
                datetime.now(),
                media,
                type_recipient,
                status
            )
            self.session.add(new_mailing)
            await self.session.commit()

    async def create_task_mailing(self, mailing_id: UUID):
        async with self.session.begin():
            active_mailing = await self.gateway \
                .count_with_status(StatusMailing.PROCESS)
            if active_mailing:
                await self.session.rollback()
                raise AlreadyProcessMailing
            
            mailing = await self.gateway \
                .query_mailing_with_id(mailing_id)
            if mailing["type_recipient"] in [
                RecipientMailing.FREE, RecipientMailing.TRAINING
            ]:
                is_exists = False
            else:
                is_exists = True
            recipiens_ids = await self.gateway \
                .query_all_user_id_with_role(is_exists=is_exists)
            
            kbd = None
            if mailing["type_recipient"] == RecipientMailing.TRAINING:
                builder = InlineKeyboardBuilder()
                builder.button(text="Все тренировки", callback_data="from_mailing")
                kbd = builder.as_markup(resize_keyboard=True)
            task = partial(
                send_mailing_message, 
                users_ids=recipiens_ids, 
                mailing_id=mailing_id,
                mailing_media=mailing["media"], 
                mailing_text=mailing["text"],
                kbd=kbd
            )
            await self.gateway.update_status_mailing(
                mailing_id, StatusMailing.PROCESS
            )
            await self.session.commit()
            return task
        
    async def update_name_mailing(self, mailing_id: UUID, name: str) -> None:
        async with self.session.begin():
            await self.gateway.update_name(name, mailing_id)
            await self.session.commit()

    async def delete_mailing(self, mailing_id: UUID) -> None:
        async with self.session.begin():
            await self.gateway.delete(mailing_id)
            await self.session.commit()