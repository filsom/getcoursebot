from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.orm import registry, composite, relationship, column_property

from getcoursebot.domain.model.day_menu import AdjustedIngredient, AdjustedRecipe, DayMenu, Ingredient, Recipe
from getcoursebot.domain.model.proportions import KBJU, Proportions
from getcoursebot.domain.model.training import Category, LikeTraining, MaillingMedia, Malling, Media, Photos, Training
from getcoursebot.domain.model.user import Role, NameRole, User


metadata = sa.MetaData()
mapper = registry()


mailling_table = sa.Table(
    "maillings",
    metadata,
    sa.Column('mailling_id', sa.UUID, primary_key=True, nullable=False),
    sa.Column('mailling_roles', sa.ARRAY(sa.Integer), nullable=False),
    sa.Column('text', sa.String(4000), nullable=False),
    sa.Column('planed_in', sa.DATE, nullable=False),
)


users_table = sa.Table(
    'users',
    metadata,
    sa.Column('email', sa.String(100), primary_key=True, nullable=False),
    sa.Column('user_id', sa.BigInteger, index=True, nullable=False),
    sa.Column('norma_kkal', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('b', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('j', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('u', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('age', sa.Integer, nullable=True),
    sa.Column('height', sa.Integer, nullable=True),
    sa.Column('weight', sa.Integer, nullable=True),
    sa.Column('coefficient', sa.String(100), nullable=True),
    sa.Column('target_procent', sa.String(100), nullable=True),
    sa.Column('on_view', sa.Boolean, nullable=False, default=False),
)


users_roles_table = sa.Table(
    "users_roles",
    metadata,
    sa.Column('email', sa.ForeignKey('users.email', onupdate="CASCADE"), primary_key=True, nullable=False),
    sa.Column('role_id', sa.ForeignKey('roles.role_id'), primary_key=True, nullable=False),
)

@dataclass
class UsersRoles:
    email: str
    role_id: int


roles_table = sa.Table(
    'roles',
    metadata,
    sa.Column('role_id', sa.Integer, primary_key=True, nullable=False),
    sa.Column('name', sa.String(20), nullable=False)
)


recipes_table = sa.Table(
    'recipes',
    metadata,
    sa.Column('recipe_id', sa.Integer, primary_key=True, nullable=False),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('recipe', sa.String, nullable=False),
    sa.Column('photo_id', sa.String, nullable=False),
    sa.Column('amount_kkal', sa.DECIMAL(20, 0), nullable=False),
    sa.Column('b', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('j', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('u', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('type_meal', sa.Integer, nullable=False),
)


ingredients_table = sa.Table(
    'ingredients',
    metadata,
    sa.Column('oid', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('recipe_id', sa.ForeignKey('recipes.recipe_id'), nullable=False),
    sa.Column('name', sa.String(500), nullable=False),
    sa.Column('value', sa.DECIMAL(20, 0), nullable=False),
    sa.Column('unit', sa.String, nullable=False),
)


adjusted_ingredients_table = sa.Table(
    'adjusted_ingredients',
    metadata,
    sa.Column('oid', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('recipe_id', sa.ForeignKey('adjusted_recipes.recipe_id'), nullable=False),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('value', sa.DECIMAL(20, 0), nullable=False),
    sa.Column('unit', sa.String, nullable=False),
)


adjusted_recipes_table = sa.Table(
    'adjusted_recipes',
    metadata,
    sa.Column('oid', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('recipe_id', sa.Integer, nullable=False),
    sa.Column('menu_id', sa.ForeignKey('day_menu.menu_id'), nullable=False),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('recipe', sa.String, nullable=False),
    sa.Column('photo_id', sa.String, nullable=False),
    sa.Column('amount_kkal', sa.DECIMAL(20, 0), nullable=False),
    sa.Column('type_meal', sa.Integer, nullable=False),
)


day_menu_table = sa.Table(
   'day_menu',
    metadata,
    sa.Column('menu_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('user_id', sa.ForeignKey('users.user_id'), nullable=False),
    sa.Column('created_at', sa.DATE, nullable=False),
    sa.Column('my_snack_kkal', sa.DECIMAL(20, 0), nullable=True),
)


like_training_table = sa.Table(
   'like_training',
    metadata,
    sa.Column('like_id', sa.UUID, default=uuid4, primary_key=True, nullable=False),
    sa.Column('training_id', sa.ForeignKey('trainigs.training_id'), nullable=False),
    sa.Column('user_id', sa.ForeignKey('users.user_id'), nullable=False),
)


trainigs_table = sa.Table(
    'trainigs',
    metadata,
    sa.Column('training_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('category_id', sa.ForeignKey('categories.category_id'), nullable=False),
    sa.Column('text', sa.String(3000), nullable=False),
    sa.Column('created_at', sa.DateTime, nullable=False),
)


medias_table = sa.Table(
    'medias',
    metadata,
    sa.Column('media_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('training_id', sa.ForeignKey('trainigs.training_id'), nullable=False),
    sa.Column('file_id', sa.String(200), nullable=False),
    sa.Column('file_uniq_id', sa.String(100), nullable=False),
    sa.Column('message_id', sa.Integer, nullable=False),
    sa.Column('content_type', sa.String, nullable=False)
)


malling_medias_table = sa.Table(
    'malling_medias',
    metadata,
    sa.Column('media_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('mailling_id', sa.ForeignKey('maillings.mailling_id', ondelete="CASCADE"), nullable=False),
    sa.Column('file_id', sa.String(200), nullable=False),
    sa.Column('file_uniq_id', sa.String(100), nullable=False),
    sa.Column('message_id', sa.Integer, nullable=False),
    sa.Column('content_type', sa.String, nullable=False)
)


categories_table = sa.Table(
    'categories',
    metadata,
    sa.Column('category_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('name', sa.String(30), nullable=False),
)


def mappers(mapper: registry):
    mapper.map_imperatively(
        MaillingMedia,
        malling_medias_table
    )
    mapper.map_imperatively(
        Malling,
        mailling_table,
        properties={
            "photos": relationship(MaillingMedia, lazy='joined')
        }
    )
    mapper.map_imperatively(
        UsersRoles,
        users_roles_table
    )
    mapper.map_imperatively(
        LikeTraining,
        like_training_table
    )
    mapper.map_imperatively(
        Media,
        medias_table
    )
    mapper.map_imperatively(
        Role,
        roles_table,
    )
    mapper.map_imperatively(
        Category,
        categories_table
    )
    mapper.map_imperatively(
        Training,
        trainigs_table,
        properties={
            'videos': relationship(Media, lazy='joined', default_factory=list)
        }
    )
    mapper.map_imperatively(
        User,
        users_table,
        properties={
            'user_id': users_table.c.user_id,
            'kbju': composite(
                KBJU,
                users_table.c.b,
                users_table.c.j,
                users_table.c.u
            ),
            "roles": relationship(
                Role,
                secondary=users_roles_table,
                primaryjoin="User.email == UsersRoles.email",
                secondaryjoin="UsersRoles.role_id == Role.role_id",
                lazy='joined'
            ),
            "_proportions": users_table.c.age,
            "proportions": composite(
                Proportions,
                users_table.c.age,
                users_table.c.height,
                users_table.c.weight,
                users_table.c.coefficient,
                users_table.c.target_procent
            )
        }
    )
    mapper.map_imperatively(
        Ingredient,
        ingredients_table
    )
    mapper.map_imperatively(
        AdjustedIngredient,
        adjusted_ingredients_table
    )
    mapper.map_imperatively(
        Recipe,
        recipes_table,
        properties={
            'kbju': composite(
                KBJU,
                recipes_table.c.b,
                recipes_table.c.j,
                recipes_table.c.u
            ),
            'ingredients': relationship(Ingredient, lazy="joined")
        }
    )
    mapper.map_imperatively(
        AdjustedRecipe,
        adjusted_recipes_table,
        properties={
            'ingredients': relationship(AdjustedIngredient, lazy="joined")
        }
    )
    mapper.map_imperatively(
        DayMenu,
        day_menu_table,
        properties={
            'my_recepts': relationship(AdjustedRecipe, lazy="joined")
        }
    )

@sa.event.listens_for(User, 'load')
def load_seller(user, value):
    if user._proportions is None:
        user.proportions = None
        user.kbju = None

@sa.event.listens_for(DayMenu, 'load')
def load_seller(menu, value):
    if menu.my_recepts is None:
        menu.my_recepts = []