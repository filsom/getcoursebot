from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.orm import registry, composite, relationship

from getcoursebot.domain.model.day_menu import DayMenu, Ingredient, Recipe
from getcoursebot.domain.model.proportions import KBJU, Proportions
from getcoursebot.domain.model.training import Category, LikeTraining, MailingMedia, Mailing, Media, Training
from getcoursebot.domain.model.user import Role, User


metadata = sa.MetaData()
mapper = registry()


users_table = sa.Table(
    'users',
    metadata,
    sa.Column('user_id', sa.BigInteger, primary_key=True, nullable=False),
    sa.Column('email', sa.String, unique=True, nullable=False),
    sa.Column('norma_kkal', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('b', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('j', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('u', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('age', sa.Integer, nullable=True),
    sa.Column('height', sa.Integer, nullable=True),
    sa.Column('weight', sa.Integer, nullable=True),
    sa.Column('coefficient', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('target_procent', sa.DECIMAL(20, 0), nullable=True),
    sa.Column('on_view', sa.Boolean, nullable=False, default=False),
)


roles_table = sa.Table(
    "roles",
    metadata,
    sa.Column('oid', sa.BigInteger, primary_key=True, autoincrement=True, nullable=False),
    sa.Column('email', sa.String, unique=False),
    sa.Column('group_id', sa.Integer, nullable=False),
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


training_medias_table = sa.Table(
    'trainings_medias',
    metadata,
    sa.Column('media_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('training_id', sa.ForeignKey('trainigs.training_id', ondelete="CASCADE"), nullable=False),
    sa.Column('file_id', sa.String(200), nullable=False),
    sa.Column('file_unique_id', sa.String(100), nullable=False),
    sa.Column('message_id', sa.Integer, nullable=False),
    sa.Column('content_type', sa.String, nullable=False)
)


mailing_table = sa.Table(
    "mailings",
    metadata,
    sa.Column('mailing_id', sa.UUID, primary_key=True, nullable=False),
    sa.Column('text', sa.String(4000), nullable=False),
    sa.Column('name', sa.String(128), nullable=True),
    sa.Column('planed_in', sa.DateTime, nullable=False),
    sa.Column('type_recipient', sa.Integer, nullable=False),
    sa.Column('status', sa.String(20), nullable=False),
)


mailing_medias_table = sa.Table(
    'malling_medias',
    metadata,
    sa.Column('media_id', sa.UUID, primary_key=True, default=uuid4, nullable=False),
    sa.Column('mailing_id', sa.ForeignKey('mailings.mailing_id', ondelete="CASCADE"), nullable=False),
    sa.Column('file_id', sa.String(200), nullable=False),
    sa.Column('file_unique_id', sa.String(100), nullable=False),
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
        MailingMedia,
        mailing_medias_table
    )
    mapper.map_imperatively(
        Mailing,
        mailing_table,
        properties={
            "media": relationship(MailingMedia, lazy='joined')
        }
    )
    mapper.map_imperatively(
        LikeTraining,
        like_training_table
    )
    mapper.map_imperatively(
        Media,
        training_medias_table
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
            'norma_kkal': users_table.c.norma_kkal,
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


@sa.event.listens_for(User, 'load')
def load_seller(user, value):
    if user._proportions is None:
        user.proportions = None
        user.kbju = None

@sa.event.listens_for(DayMenu, 'load')
def load_seller(menu, value):
    if menu.my_recepts is None:
        menu.my_recepts = []