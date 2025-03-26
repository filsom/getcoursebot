import aiohttp
import asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.sqlite import insert
# from getcoursebot.domain.model.user import IDRole
# from getcoursebot.port.adapter.orm import users_roles_table


BASE_URL = "https://workoutmila.ru/pl/api/account"
ACCESS_KEY = "qZ2MZ3kHUxzFZpp4JJvzBQOWeQd1f9hwafDixfBWoYbpQp7OCqcDu6H0PBDQbcqw2JC5LCAVKdK1epLPsFFopntOUHHxtODgQqSxhJlQkjCFvfYio1NCiy98g09p9hDT"  # Замените на ваш ключ доступа
GROUP_IDS = [2315673, 3088338] 
MAP = {2315673: 3, 3088338: 2}

async def fetch_exports_id(session, group_id, access_key):
    url = f"{BASE_URL}/groups/{group_id}/users"
    params = {
        "key": access_key,
        "status": "active"
    }
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            print(data)
            exports_id = data["info"]["export_id"]
            if exports_id:
                return group_id, exports_id 
            else:
                raise ValueError(f"[Group {group_id}] В ответе отсутствует exports_id")
        else:
            raise Exception(f"[Group {group_id}] Ошибка при получении exports_id: {response.status}")


async def fetch_export_data(session, group_id, exports_id, access_key):
    url = f"{BASE_URL}/exports/{exports_id}"
    params = {
        "key": access_key
    }
    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            print(data)
            group = MAP.get(group_id)
            result = (group, [])
            for item in data["info"]:
                print(item)
                # result[1].append({"email": item[1]})
                # result
        else:
            raise Exception(f"[Group {group_id}] Ошибка при получении данных: {response.status}")


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for group_id in GROUP_IDS:
            tasks.append(asyncio.create_task(fetch_exports_id(session, group_id, ACCESS_KEY)))

        exports = await asyncio.gather(*tasks)
        print(exports)
        # await asyncio.sleep(7)
        # tasks.clear()
        # for export in [(2315673, 64399772), (3088338, 64399771)]:
            # tasks.append(asyncio.create_task(fetch_export_data(session, export[1], export[0], ACCESS_KEY)))
            # await fetch_export_data(session, export[1], export[0], ACCESS_KEY)
        # result = await asyncio.gather(*tasks)
        # print(result)
        # tasks.clear()
        # for item in result:
        #     async with AsyncSession(engine) as session:
        #         insert_ = insert(users_roles_table).values(item[1])
        #         on = insert_.on_conflict_do_update(
        #             index_elements=["email"],
        #             set_=dict()
        #         )



    


# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())