import datetime
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_dialog.api.entities import MediaAttachment
from getcoursebot.domain.model.day_menu import DayMenu, Recipe
from getcoursebot.domain.model.training import Category, Malling, Training
from getcoursebot.domain.model.user import IDRole, User
from getcoursebot.port.adapter.orm import (
    users_table, 
    roles_table, 
    categories_table,
    like_training_table,
    users_roles_table,
    day_menu_table,
    recipes_table,
    mailling_table
)


class QueryService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session

    async def delete_malling(self, malling_id):
        new = sa.delete(Malling).where(Malling.mailling_id == malling_id)
        await self.session.execute(new)
        await self.session.commit()

    async def get_malling_and_delete(self, id):
        stmt = (
            sa.select(Malling).where(Malling.mailling_id == id)
        )
        re = await self.session.execute(stmt)
        m = re.scalar()
        return m
    
    async def query_mailling(self):
        # for 
        # if data["mailling_status"] == "Платный":
        #     data["mailling_status"] = "платным"
        # else:
        #     data["mailling_status"] = "бесплатным"
        stmt = (
            sa.select(Malling)
        )
        result = await self.session.execute(stmt)
        mall = result.scalars().unique()
        x = []
        for i in mall:
            if IDRole.Free in i.mailling_roles:
                status = "бесплатным"
            else:
                status = "платным"
            x.append((status, i.planed_in, i.mailling_id))
        return {
            "planed": x
        }

    async def query_users_all_with_role(self, roles: list):
        print(roles)
        user_role_ids = (
            sa.select(users_roles_table.c.email)
            .where(users_roles_table.c.role_id.in_(roles))
        )
        res = await self.session.execute(user_role_ids)
        emails = res.scalars().all()
        print(emails)
        new_stmt = (
            sa.select(users_table.c.user_id)
            .where(users_table.c.email.in_(emails))
        )
        rows = await self.session.execute(new_stmt)
        # print(rows.scalars())
        return rows.scalars().all()

    async def query_training(self, user_id: int, category_id: UUID) -> dict:
        new_stmt = (
            sa.select(Training)
            .where(Training.category_id == category_id)
            .order_by(sa.func.random())
            .limit(1)
        )
        result = await self.session.execute(new_stmt)
        training = result.scalar()
        like_stmt = (
            sa.select(like_training_table.c.like_id)
            .where(like_training_table.c.training_id == training.training_id)
            .where(like_training_table.c.user_id == user_id)
        )
        row_result_1 = await self.session.execute(like_stmt)
        row = row_result_1.scalar()
        if row is not None:
            row_result = True
        else:
            row_result = False

        return {
            "training": training,
            "is_like": row_result
        }

    async def query_categories(self) -> dict:
        new_stmt = sa.select(categories_table)
        rows = await self.session.execute(new_stmt)
        categories = []
        for row in rows:
            if row.category_id:
                categories.append((row.name, row.category_id))
        print(categories)
        return {
            "categories": categories,
            "count": len(categories)
        }

    async def query_roles_with_id(self, user_id: int) -> dict:
        new_stmt = (
            sa.select(User)
            .where(User.user_id == user_id)
        )
        result = await self.session.execute(new_stmt)
        user = result.scalar()
        roles = []
        try:
            for row in user.roles:
                roles.append(row.name)
            return {
                "email": user.email,
                "roles": roles,
                "on_view": user.on_view
            }
        except AttributeError:
            return {
                "email": None,
                "roles": [],
                "on_view": None
            }
        
    async def query_users(self, user_id: int) -> User:
        new_stmt = (
            sa.select(User)
            .where(User.user_id == user_id)
        )
        result = await self.session.execute(new_stmt)
        user = result.scalar()
        if user is None:
            return None
        list_role_names = []
        for role in user.roles:
            list_role_names.append(role.name)

        if user.kbju is None:
            return {
                "user_id": user.user_id,
                "kkal": None,
                "b": None,
                "j": None,
                "u": None,
                "menu": False,
                "roles": list_role_names,
                "text": "У меня нет ваших данных КБЖУ.\nХотите посчитать или ввести свои данные?"
            }
        return {
            "user_id": user.user_id,
            "kkal": user.norma_kkal,
            "b": user.kbju.b,
            "j": user.kbju.j,
            "u": user.kbju.u,
            "menu": True,
            "roles": list_role_names,
            "text": "Вот что мы можем сделать 👇"
        }
        
    async def query_roles_with_email(self, email: int) -> dict:
        new_stmt = (
            sa.select(User)
            .where(User.email == email)
        )
        result = await self.session.execute(new_stmt)
        user = result.scalar()
        roles = []
        try:
            for row in user.roles:
                roles.append(row.name)
            return {
                "sub_user_id": user.user_id,
                "sub_email": user.email,
                "roles": roles,
                "on_view": user.on_view
            }
        except AttributeError:
            return {
                "sub_user_id": None,
                "sub_email": None,
                "roles": [],
                "on_view": None
            }
        
    async def update_on_view_status(self, user_id: int, on_view: bool):
        async with self.session.begin():
            new_stmt = (
                sa.update(users_table)
                .values(on_view=on_view)
                .where(users_table.c.user_id == user_id)
            )
            await self.session.execute(new_stmt)
            await self.session.commit()

    async def insert_like(self, user_id: int, training_id: UUID):
        async with self.session.begin():
            new_stmt = (
                sa.insert(like_training_table)
                .values(
                    like_id=uuid4(),
                    training_id=training_id,
                    user_id=user_id
                )
            )
            await self.session.execute(new_stmt)
            await self.session.commit()

    async def insert_role(self, email: str, role_id: int):
        async with self.session.begin():
            new_stmt = (
                sa.insert(users_roles_table)
                .values(
                    email=email,
                    role_id=role_id,
                )
            )
            await self.session.execute(new_stmt)
            await self.session.commit()

    async def delete_role(self, email: str, role_id: int):
        async with self.session.begin():
            new_stmt = (
                sa.delete(users_roles_table)
                .where(users_roles_table.c.email == email)
                .where(users_roles_table.c.role_id == role_id)
            )
            await self.session.execute(new_stmt)
            await self.session.commit()

    async def update_user_email(self, old_email: str, new_email: str):
        async with self.session.begin():
            new_stmt = (
                sa.update(users_table)
                .values(email=new_email)
                .where(users_table.c.email == old_email)
            )
            await self.session.execute(new_stmt)
            await self.session.commit()

    async def query_status_exists(self, email: str) -> bool:
        new_stmt = (
            sa.select(users_table.c.user_id)
            .where(users_table.c.email == email)
        )
        row = await self.session.execute(new_stmt)
        if row is None:
            return False
        
        return True
    
    async def query_for_menu(self, meal: str) -> dict:
        new_stmt = sa.select(Recipe).where(Recipe.type_meal == meal).order_by(sa.func.random()).limit(1)
        result = await self.session.execute(new_stmt)
        recipe = result.scalar()
        list_ingredients = []
        list_g = []
        for ingredient in recipe.ingredients:
            list_ingredients.append(f"🔹 {ingredient.name.title()}\n")
            list_g.append(f"{ingredient.value}{ingredient.unit}")

        return {
            "recipe_id": recipe.recipe_id,
            "name": recipe.name,
            "recipe": recipe.recipe,
            "photo_id": recipe.photo_id,
            "amount_kkal": recipe.amount_kkal,
            "b": recipe.kbju.b,
            "j": recipe.kbju.j,
            "u": recipe.kbju.u,
            "type_meal": recipe.type_meal,
            "ingredients": list_ingredients,
            "g": list_g,
            "class": recipe
        }
    
    async def query_day_menu_id(self, user_id: int, date: datetime) -> dict | None:
        new_stmt = (
            sa.select(day_menu_table)
            .where(day_menu_table.c.user_id == user_id)
            .where(day_menu_table.c.created_at == sa.cast(date, sa.DATE))
        )
        rows = await self.session.execute(new_stmt)
        for row in rows:
            try:
                return {
                    "user_id": user_id,
                    "menu_id": row.menu_id
                }
            except AttributeError:
                return {
                    "user_id": user_id,
                    "menu_id": None
                }
        return {
            "user_id": user_id,
            "menu_id": None
        }
    
    async def query_day_meny(self, user_id: int, date: datetime.date) -> DayMenu:
        new_stmt = (
            sa.select(DayMenu)
            .where(DayMenu.user_id == user_id)
            .where(DayMenu.created_at == date)
        )
        result = await self.session.execute(new_stmt)
        menu = result.unique()
        if menu is None:
            return None
        return menu.scalar()
        
