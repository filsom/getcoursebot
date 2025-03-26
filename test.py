# import aiohttp
# import asyncio

# # Константы для доступа к API
# BASE_URL = "https://workoutmila.ru/pl/api/account"
# ACCESS_KEY = "qZ2MZ3kHUxzFZpp4JJvzBQOWeQd1f9hwafDixfBWoYbpQp7OCqcDu6H0PBDQbcqw2JC5LCAVKdK1epLPsFFopntOUHHxtODgQqSxhJlQkjCFvfYio1NCiy98g09p9hDT"  # Замените на ваш ключ доступа
# GROUP_IDS = [2315673, 3088338]  # Список group_id

# async def fetch_exports_id(session, group_id, access_key):
#     """
#     Отправляет запрос для получения exports_id.
#     """
#     url = f"{BASE_URL}/groups/{group_id}/users"
#     params = {
#         "key": access_key,
#         "status": "active"
#     }
#     async with session.get(url, params=params) as response:
#         if response.status == 200:
#             data = await response.json()
#             exports_id = data["info"]["export_id"] # Предполагается, что exports_id находится в ответе
#             if exports_id:
#                 print(f"[Group {group_id}] Получен exports_id: {exports_id}")
#                 return exports_id
#             else:
#                 raise ValueError(f"[Group {group_id}] В ответе отсутствует exports_id")
#         else:
#             raise Exception(f"[Group {group_id}] Ошибка при получении exports_id: {response.status}")

# async def fetch_export_data(session, group_id, exports_id, access_key):
#     """
#     Отправляет запрос для получения данных по exports_id.
#     """
#     url = f"{BASE_URL}/exports/{exports_id}"
#     params = {
#         "key": access_key
#     }
#     async with session.get(url, params=params) as response:
#         if response.status == 200:
#             data = await response.json()
#             print(f"[Group {group_id}] Получены данные по exports_id: {data}")
#             return group_id, data
#         else:
#             raise Exception(f"[Group {group_id}] Ошибка при получении данных: {response.status}")

# async def process_group_sequentially(session, group_id, access_key):
#     """
#     Обрабатывает один group_id последовательно: получает exports_id и затем данные.
#     """
#     try:
#         # Шаг 1: Получаем exports_id
#         exports_id = await fetch_exports_id(session, group_id, access_key)
#         await asyncio.sleep(60)
#         # Шаг 2: Получаем данные по exports_id
#         group_id, export_data = await fetch_export_data(session, group_id, exports_id, access_key)
        
#         # Возвращаем результат для этой группы
#         return group_id, export_data
#     except Exception as e:
#         print(f"[Group {group_id}] Произошла ошибка: {e}")
#         return group_id, None

# async def main():
#     """
#     Основная функция, которая управляет асинхронными операциями для всех групп.
#     """
#     async with aiohttp.ClientSession() as session:
#         results = {}
#         for group_id in GROUP_IDS:
#             print(f"Обработка группы: {group_id}")
#             group_id, data = await process_group_sequentially(session, group_id, ACCESS_KEY)
#             if data is not None:
#                 results[group_id] = data

#             await asyncio.sleep(30)
#         # Вывод итоговых результатов
#         print("\nИтоговые результаты:")
#         for group_id, data in results.items():
#             print(f"Группа {group_id}: {data}")

# # Запуск программы
# if __name__ == "__main__":
#     asyncio.run(main())


class Group(object):
    ADMIN = 1
    FOOD = 2315673
    TRAINING = 3088338


class AccessGC:
    def __init__(self, groups: list[Group]):
        self.groups = groups

    def check_group(self, value: Group) -> bool:
        if not self.groups:
            return False
        
        for group in self.groups:
            if group == value or group == Group.ADMIN:
                return True
        return False
    
    def groups_empty(self) -> bool:
        if not self.groups:
            return True
        
        return False