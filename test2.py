import asyncio
from aiohttp import ClientSession

GROUPS = [2315673, 3088338]
ACCESS_KEY = "qZ2MZ3kHUxzFZpp4JJvzBQOWeQd1f9hwafDixfBWoYbpQp7OCqcDu6H0PBDQbcqw2JC5LCAVKdK1epLPsFFopntOUHHxtODgQqSxhJlQkjCFvfYio1NCiy98g09p9hDT"


async def get_export_key(
    access_key: str, 
    group_id: str, 
    client: ClientSession
):
    MAP_GROUP = {
        2315673: "Food",
        3088338: "Training",
    }
    async with client.get(
        f"https://workoutmila.ru/pl/api/account/groups/{group_id}/users?key={access_key}&status=active"
    ) as response:
        response_export = await response.json()
        export_id = response_export["info"]["export_id"]
        return export_id
        # async with client.get(
        #     f"https://workoutmila.ru/pl/api/account/exports/{export_id}?key={access_key}"
        # ) as response:
        #     list_items = {"role": MAP_GROUP.get(group_id)}
        #     list_items.setdefault("emails", [])
        #     for item in response["info"]["items"]:
        #         list_items["emails"].append(item[1].lower())
        #     return list_items
        

async def main():
    async with ClientSession() as client:
        async with client.get("https://workoutmila.ru/pl/api/account/exports/64471265?key=qZ2MZ3kHUxzFZpp4JJvzBQOWeQd1f9hwafDixfBWoYbpQp7OCqcDu6H0PBDQbcqw2JC5LCAVKdK1epLPsFFopntOUHHxtODgQqSxhJlQkjCFvfYio1NCiy98g09p9hDT") as response:
            x = await response.json()
            for i in x["info"]["items"]:
                print(i[1])


    # async with ClientSession() as client:
    #     tasks = []
    #     for i in [2315673, 3088338]:
    #         tasks.append(asyncio.create_task(
    #             get_export_key(
    #                 "qZ2MZ3kHUxzFZpp4JJvzBQOWeQd1f9hwafDixfBWoYbpQp7OCqcDu6H0PBDQbcqw2JC5LCAVKdK1epLPsFFopntOUHHxtODgQqSxhJlQkjCFvfYio1NCiy98g09p9hDT",
    #                 i,
    #                 client
    #             )
    #         ))

        # print(await asyncio.gather(*tasks))


async def get_export_id(client: ClientSession):


async def parse_gc_group(engine): 
    for group_id in GROUPS:
        async with ClientSession() as client:
            async with client.get(
                f"https://workoutmila.ru/pl/api/account/groups/{group_id}/users?key={ACCESS_KEY}&status=active"
            ) as response:
                


if __name__ == "__main__":
    asyncio.run(main())


# import asyncio
# import sqlalchemy as sa
# from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
# from aiohttp import ClientSession


# async def parse_gc_groups(
#     access_key: str,
#     groups_ids: list,
#     engine: AsyncEngine, 
# ):
#     async with ClientSession() as client:
#         request_export = [
#             get_export_key(access_key, group_id) for group_id in groups_ids
#         ]
#         result = asyncio.gather(*request_export)
#         requests_user = [
#             get_users_email(*u, access_key, client) for u in result
#         ]
#         print(requests_user)


# async def get_export_key(
#     access_key: str, 
#     group_id: str, 
#     client: ClientSession
# ):
#     async with client.get(
#         f"https://workoutmila.ru/pl/api/account/groups/{group_id}/users?key={access_key}&status=active"
#     ) as response:
#         response_export = await response.json()
#         if not response_export["status"]:
#             return (None, group_id)
#         else:
#             export_id = response_export["info"]["export_id"]
#             return (export_id, group_id)
        

# async def get_users_email(exports_id: int, group_id: int, access_key: str, client: ClientSession):
#         MAP_GROUP = {
#             2315673: 1,
#             3088338: 2,
#         }
#         async with client.get(
#             f"https://workoutmila.ru/pl/api/account/exports/{exports_id}?key={access_key}"
#         ) as response:
#             list_items = {"role": MAP_GROUP.get(group_id)}
#             list_items.setdefault("emails", [])
#             for item in response["info"]["items"]:
#                 list_items["emails"].append(item[1].lower())
#             return list_items

# async def update_status(engine: AsyncEngine):
#     async with AsyncSession(engine) as session:
#         async with session.begin():
#             update_stmt = (
#                 sa.insert
#             )


# if __name__ == "__main__":
#     asyncio.run(parse_gc_groups(
#         "qZ2MZ3kHUxzFZpp4JJvzBQOWeQd1f9hwafDixfBWoYbpQp7OCqcDu6H0PBDQbcqw2JC5LCAVKdK1epLPsFFopntOUHHxtODgQqSxhJlQkjCFvfYio1NCiy98g09p9hDT",
#         [2315673, 3088338],
        
#     ))

# "export_id": 64340392
# '64340103' 
# if __name__ == "__main__":
#     asyncio.run(main())




# import re

# def format_recipe(text):
#     # Удаляем смайлики и лишние символы
#     text = re.sub(r'[()]', '', text)
#     text = re.sub(r'\s+', ' ', text).strip()
    
#     # Исправляем пунктуацию
#     text = re.sub(r'\s*([,;.])', r'\1', text)
#     text = re.sub(r',\s*,', ',', text)
#     text = re.sub(r'\s*\.\s*', '. ', text)
    
#     # Разделяем на предложения
#     sentences = [s.strip().capitalize() for s in re.split(r'(?<=[.!?])\s+', text)]
    
#     # Формируем итоговый текст
#     formatted = "\n".join(f"• {s}" if not s.endswith((')', '.')) else s for s in sentences)
#     formatted = re.sub(r'• (\w)', lambda m: f"• {m.group(1).upper()}", formatted)
    
#     # Добавляем завершающий штрих
#     return f"Рецепт:\n\n{formatted}\n\nПриятного приготовления! 🍳"

# # Пример использования
# raw_text = """Кабачок трём на мелкой тёрте, добавляем яйца , молоко , зелень и сыр )
# хорошо перемешиваем)
# дальше добавляем муку) ,специи,соль перец по вкусу .
# жарим блинчики на сковороде смазанной каплей масла с двух сторон по 2 минутки)
# с начинкой можно экспериментировать"""

# print(format_recipe(raw_text))