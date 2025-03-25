from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Media:
    message_id: int
    file_id: str
    file_uniq_id: str
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
class MaillingMedia:
    message_id: int
    file_id: str
    file_uniq_id: str
    content_type: str

    

@dataclass
class Malling:
    mailling_id: int
    mailling_roles: list
    text: str
    planed_in: datetime
    photos: list[MaillingMedia]