from enum import Enum

from app import app
from app.models import MyCompany


def get_my_company():
    with app.app_context():
        return MyCompany.query.filter_by(name='АО "СПЕЦАВТОБАЗА №1"').first()


class NDSRate(Enum):
    null = 0
    ten = 10
    twenty = 20
