from datetime import datetime

from sqlalchemy import Column, String, Text

from app.models.base import CharityBase


def time_now():
    return datetime.now()


class CharityProject(CharityBase):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
