from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from getcoursebot.domain.model.day_menu import DayMenu, Recipe
from getcoursebot.domain.model.training import Category, Training
from getcoursebot.domain.model.user import IDRole, Role, NameRole, User
from getcoursebot.port.adapter.orm import users_table, roles_table, recipes_table


class UserRepositories:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(user)

    async def add_role(self, ) -> None:
        self._session.add()

    async def with_email(self, email: str) -> User | None:
        stmt = sa.select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def with_id(self, user_id: str) -> User | None:
        stmt = sa.select(User).where(User.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar()

    async def users_id_with_role(self, role: NameRole) -> list[int]:
        stmt = sa.select(users_table.c.user_id).where(sa.and_(
            users_table.c.user_id != None,
            users_table.c.role == role
        ))
        result = await self._session.execute(stmt)
        return result.scalars()


class RecipeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, recipe: Recipe) -> None:
        self._session.add(recipe)

    async def with_ids(self, recipe_ids: list[UUID]) -> list[Recipe]:
        stmt = sa.select(Recipe).where.in_(recipe_ids)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add_menu(self, menu: DayMenu) -> None:
        self._session.add(menu)

    async def menu_with_id_and_time(
        self, user_id: int, current_time: datetime
    ) -> DayMenu | None:
        stmt = sa.select(DayMenu).where(sa.and_(
            DayMenu.user_id == user_id, 
            DayMenu.created_at == current_time
        ))
        result = await self._session.execute(stmt)
        return result.scalar()
    
    async def query_recipe_count(self) -> dict:
        my_table = sa.table("recipes", sa.column("recipe_id"))
        new_stmt = (
            sa.select(sa.func.count()).select_from(my_table)
        )
        row = await self._session.execute(new_stmt)
        if not row:
            return 1
        
        return row.scalar()
    

class TrainingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, training: Training) -> None:
        self._session.add(training)

    async def last(self) -> Training:
        stmt = sa.select(Training).order_by(Training.created_at).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar()
    
    async def all_categories(self) -> list[Category]:
        stmt = sa.select(Category)
        result = await self._session.execute(stmt)
        return result.scalars()
    
    async def add_category(self, category: Category) -> None:
        self._session.add(category)

    async def get_random_training(self) -> Training:
        stmt = sa.select(Training).order_by(sa.func.random()).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar()
    
    async def get_category_with_name(self, name: str) -> Category:
        stmt = (
            sa.select(Category).where(Category.name == name)
        )
        result = await self._session.execute(stmt)
        return result.scalar()