from typing import AsyncGenerator, AsyncIterable

from gspread import Spreadsheet, service_account, Client
from dishka import Provider, Scope, from_context, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from getcoursebot.application.fitness_service import FitnessService
from getcoursebot.port.adapter.aiogram.dialogs.query_service import QueryService
from getcoursebot.port.adapter.repositories import RecipeRepository, UserRepositories, TrainingRepository


class DependencyProvider(Provider):
    engine = from_context(
        provides=AsyncGenerator[AsyncEngine, None], 
        scope=Scope.APP
    )

    @provide(scope=Scope.APP)
    async def get_sheets(self) -> Spreadsheet:
        cleint = service_account("/Users/filippsomov/Desktop/getcoursebot/credentials.json")
        return cleint.open_by_key("14RajqHw2lq9_2QRzyqgB9K7f2oiiVHhLlWrZnkz5vvE")
    
    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, 
        engine: AsyncGenerator[AsyncEngine, None]
    ) -> AsyncIterable[AsyncSession]:
        async with AsyncSession(engine) as session:
            yield session
    
    @provide(scope=Scope.REQUEST)
    async def get_fitness_servise(
        self, 
        session: AsyncSession,
        table: Spreadsheet,
    ) -> FitnessService:
        return FitnessService(
            session,
            table,
            UserRepositories(session),
            RecipeRepository(session),
            TrainingRepository(session),
        )
    
    @provide(scope=Scope.REQUEST)
    async def get_query_service(
        self, 
        session: AsyncSession
    ) -> QueryService:
        return QueryService(session)