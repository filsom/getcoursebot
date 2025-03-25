import asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from aiohttp import ClientSession

from getcoursebot.domain.model.user import NameRole
from getcoursebot.port.adapter.orm import roles_table


async def parse_gc_groups(
    access_key: str,
    groups_ids: list,
    engine: AsyncEngine, 
):
    async with ClientSession() as client:
        request_export = [
            get_export_key(access_key, group_id) for group_id in groups_ids
        ]
        result = asyncio.gather(*request_export)
        requests_user = [
            get_users_email(*u, access_key, client) for u in result
        ]
        print(requests_user)


async def get_export_key(
    access_key: str, 
    group_id: str, 
    client: ClientSession
):
    async with client.get(
        f"https://workoutmila.ru/pl/api/account/groups/{group_id}/users?key={access_key}&status=active"
    ) as response:
        response_export = await response.json()
        if not response_export["status"]:
            return (None, group_id)
        else:
            export_id = response_export["info"]["export_id"]
            return (export_id, group_id)
        

async def get_users_email(exports_id: int, group_id: int, access_key: str, client: ClientSession):
        MAP_GROUP = {
            2315673: NameRole.Training,
            3088338: NameRole.Food,
        }
        async with client.get(
            f"https://workoutmila.ru/pl/api/account/exports/{exports_id}?key={access_key}"
        ) as response:
            list_items = {"role": MAP_GROUP.get(group_id)}
            list_items.setdefault("emails", [])
            for item in response["info"]["items"]:
                list_items["emails"].append(item[1].lower())
            return list_items

async def update_status(engine: AsyncEngine):
    async with AsyncSession(engine) as session:
        async with session.begin():
            update_stmt = (
                sa.insert
            )


if __name__ == "__main__":
    asyncio.run(parse_gc_groups())