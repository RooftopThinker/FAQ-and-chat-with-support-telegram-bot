import sqlalchemy
from .database import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.BigInteger, unique=True, nullable=False)
    telegram_username = sqlalchemy.Column(sqlalchemy.String)
    telegram_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    phone = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    reviews_approved = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reviews_declined = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    faq_viewed = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    instructions_viewed = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    problems_appealed = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    # bank_requisite = sqlalchemy.Column(sqlalchemy.String)