from datetime import datetime
import re
from uuid import UUID, uuid4
from gspread import Spreadsheet
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from getcoursebot.application import commands as cmd
from getcoursebot.application.error import AlreadyExists
from getcoursebot.domain.model.day_menu import Ingredient, Recipe, TypeMeal
from getcoursebot.domain.model.proportions import KBJU, Proportions
from getcoursebot.domain.model.training import Category, LikeTraining, Training
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.repositories import RecipeRepository, TrainingRepository, UserRepositories
from getcoursebot.domain.model.user import IDRole, Role, NameRole, User
from getcoursebot.port.adapter.orm import users_table, roles_table
from getcoursebot.port.adapter.aiogram.dialogs.auth import authorize


def parse_recipe(data: dict):
    TYPE_MAP = {
        "завтрак": TypeMeal.Breakfast,
        "обед": TypeMeal.Lunch,
        "ужин": TypeMeal.Dinner,
        "перекус": TypeMeal.Snack
    }
    return Recipe(
        data["id"],
        data["name"].strip().title(),
        data["recipe"].strip(),
        data["photo"],
        data["kkal"],
        KBJU(
            data["proteins"], 
            data["fat"], 
            data["carbohydrates"]
        ),
        TYPE_MAP.get(data["type"].lower()),
        normalize_ingredients(data["ingred"])
    )


def normalize_ingredients(text: str) -> Ingredient:
    normal_ingredients = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        result = parse_ingredient(line)
        ingredient = Ingredient(
            result["name"],
            result["value"],
            result["unit"]
        )
        normal_ingredients.append(ingredient)
    return normal_ingredients


def parse_ingredient(text):
    text = text.replace('\n', ' ').strip()
    pattern = r'^(\d+)_([^_\s]*)\s*(.*)$'
    match = re.match(pattern, text)
    
    if not match:
        return {
            'value': None,
            'unit': 'г',
            'name': text,
            'error': 'Некорректный формат, установлены значения по умолчанию'
        }
    
    quantity = int(match.group(1))
    raw_unit = match.group(2).strip()
    raw_name = match.group(3).strip()
    
    unit = raw_unit.lower().replace('.', '') if raw_unit else 'г'
    UNIT_MAP = {
        'гр': 'г',
        'грамм': 'г',
        'гм': 'г',
        'ml': 'мл',
        'миллилитр': 'мл',
        'л': 'л',
        'литр': 'л',
        'шт': 'шт',
        'штука': 'шт',
        'ст': 'ст',
        'стакан': 'ст',
        'чайнл': 'ч.л',
        'столл': 'ст.л',
        'чл': 'ч.л',
        'сл': 'ст.л'
    }
    unit = UNIT_MAP.get(unit, unit)
    
    name = re.sub(r'\.+$', '', raw_name).strip()
    name = name if name else 'Не указано название'
    
    return {
        'value': quantity,
        'unit': unit,
        'name': name.title()
    }


class FitnessService:
    def __init__(
        self,
        session: AsyncSession,
        table: Spreadsheet,
        user_repository: UserRepositories,
        recipe_repository: RecipeRepository,
        training_repository: TrainingRepository,
        # query_service: QueryService
    ) -> None:
        self._session = session
        self._table = table
        self._user_repository = user_repository
        self._recipe_repository = recipe_repository
        self._training_repository = training_repository
        # self._query_service = query_service

    async def create_free_user(self, user_id: int, email: str) -> None:
        async with self._session.begin():
            new_user = User(user_id, email)
            self._session.add(new_user)
            await self._session.commit()

    async def add_mailling(self, m):
        async with self._session.begin():
            self._session.add(m)
            await self._session.commit()
    
    async def upload_recipe(self):
        async with self._session.begin():
            head = await self._recipe_repository.query_recipe_count()
            data = self._table.worksheet("List1")
            rows = data.get_all_records()[head:]
            if rows:
                for row in rows:
                    res = parse_recipe(row)
                    self._session.add(res)
            await self._session.commit()

    async def view(self, email: str) -> None:
        async with self._session.begin():
            new_stmt = (
                update(roles_table)
                .where(roles_table.c.name == str(NameRole.Free))
                .where(roles_table.c.email == email)
                .values(name=NameRole.FreeLooked)
            )
            await self._session.execute(new_stmt)
            await self._session.commit()


    async def change_access(self, email: str, scope: str) -> None:
        async with self._session.begin():
            user = await self._user_repository.with_email(email)
            if user is None:
                raise ValueError

            user.roles.append(Role(email, scope))
            await self._session.commit()

    async def add_like_training(self, user_id: int, training_id: UUID) -> None:
        async with self._session.begin():
            like_training = LikeTraining(
                training_id, user_id
            )
            self._session.add(like_training)
            await self._session.commit()

    async def query_user_ids_with_role(self, role: NameRole) -> list[int]:
        async with self._session.begin():
            return await self._user_repository.users_id_with_role(role)
    
    async def add_new_category(self, user_id: int, name: str) -> None:
        async with self._session.begin():
            exists_category = await self._training_repository.get_category_with_name(name.title())
            if exists_category:
                raise AlreadyExists
            
            await self._training_repository.add_category(
                Category(uuid4(), name.title())
            )
            await self._session.commit()

    async def get_types_categories(self) -> list[Category]:
        result = await self._training_repository.all_categories()
        list_result = []
        for category in result:
            list_result.append((category.name, category.category_id))
        return list_result
        
    async def get_user_role(self, user_id: int) -> list[Role]:
        user = await self._user_repository.with_id(user_id)
        return user.roles if user is not None else None

    async def create_user(self, command: cmd.CreateUserCommand):
        async with self._session.begin():
            user = await self._user_repository.with_email(
                command.email
            )
            if user is not None:
                data = self._query_service.query_roles_with_id(
                    command.user_id
                )
                return data["roles"]
            
            new_user = User(
                command.user_id,
                command.email,
            )
            await self._user_repository.add(new_user)
            await self._session.flush()
            await self._session.commit()
            return [NameRole.Free]

    async def make_day_menu(self, command: cmd.MakeDayMenuCommand) -> None:
        async with self._session.begin():
            current_date = datetime.now().date()
            menu = await self._recipe_repository.menu_with_id_and_time(
                command.user_id, current_date
            )
            if menu:
                return
            
            user = await self._user_repository.with_id(command.user_id)
            menu = user.make_day_menu(command.recipes, current_date, command.my_snack)
            snak_kkal = menu.my_snack_kkal
            await self._recipe_repository.add_menu(menu)
            await self._session.commit()
            return snak_kkal

    async def set_proportions(self, command: cmd.CalculateDayNormCommand) -> None:
        # async with self._session.begin():
        user = await self._user_repository.with_id(command.user_id)
        user.calculate_day_norm(
            Proportions(
                command.age,
                command.height,
                command.weight,
                command.coefficient,
                command.target_procent
            )
        )
        await self._session.commit()

    async def set_input_user_data(self, command: cmd.InputeDayNormCommand) -> None:
        async with self._session.begin():
            user = await self._user_repository.with_id(command.user_id)
            user.norma_kkal = command.kkal
            user.proportions = Proportions(
                1,
                1,
                1,
                command.coefficient,
                command.target_procent
            )
            user.kbju = KBJU(
                command.b,
                command.j,
                command.u
            )
            await self._session.commit()

    async def add_training(self, command: cmd.AddTrainingCommand) -> UUID:
        async with self._session.begin():
            training_id = uuid4()
            training = Training(
                    training_id,
                    command.category_id,
                    command.text,
                    command.videos_id,
                    datetime.now()
                )
            await self._training_repository.add(training)
            await self._session.commit()