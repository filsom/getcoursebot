from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from uuid import UUID


@dataclass
class Media:
    message_id: int
    file_id: str
    file_unique_id: str
    content_type: str


@dataclass
class Training:
    training_id: UUID
    category_id: int
    text: str
    videos: list[Media]
    created_at: datetime


@dataclass
class Category:
    category_id: UUID
    name: str


@dataclass
class LikeTraining:
    training_id: UUID
    user_id: int


@dataclass
class Photos:
   photo_id: str


@dataclass
class MailingMedia:
    message_id: int
    file_id: str
    file_unique_id: str
    content_type: str


class StatusMailing(StrEnum):
    AWAIT = auto()
    PROCESS = auto()
    DONE = auto()
    

@dataclass
class Mailing:
    mailing_id: UUID
    name: str | None
    text: str
    planed_in: datetime
    media: list[MailingMedia]
    type_recipient: int
    status: StatusMailing


class RecipientMailing(object):
    TRAINING = 1
    FREE = 2
    PAID = 3
