from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal as D
from enum import Enum, StrEnum, auto
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from getcoursebot.domain.model.day_menu import DayMenu, Recipe
from getcoursebot.domain.model.proportions import KBJU, Proportions


class MaillingStatus(object):
    Paid = "Платный"
    Free = "Бесплатный"


class NameRole(object):
    Admin = "admin"
    Food = "food"
    Training = "training"
    Free = "free"


class IDRole(object):
    Admin = 1
    Food = 2
    Training = 3
    Free = 4


@dataclass
class Role:
    role_id: int
    name: str


@dataclass
class User:
    user_id: int
    email: str
    roles: list[Role] | None = None 
    norma_kkal: D | None = None
    kbju: KBJU | None = None
    proportions: Proportions | None = None
    on_view: bool = True

    def calculate_day_norm(self, proportion: Proportions) -> None:
        self.norma_kkal = abs(proportion.calculate_kkal())
        self.kbju = proportion.calculate_kbju()
        self.proportions = proportion

    def change_proportion(self, proportion: Proportions) -> None:
        self.calculate_day_norm(proportion)

    def make_day_menu(
        self, 
        recepts: list[Recipe], 
        occurred_at: datetime, 
        my_snack: bool
    ) -> DayMenu:
        if self.proportions is None:
            raise 

        menu = DayMenu(self.user_id, occurred_at, my_recepts=[])
        menu.set_positions(recepts, self.norma_kkal, my_snack)
        return menu
    
    def set_telegram_cred(self, user_id: int) -> None:
        if self.user_id is not None:
            raise 
        
        self.user_id = user_id

    def set_access(self, role_id: IDRole, name: NameRole) -> None:
        for role in self.roles:
            if role.name == name:
                return 
            
        self.roles.append(Role(role_id, name))