import sqlalchemy
from .database import SqlAlchemyBase


class Appeal(SqlAlchemyBase):
    __tablename__ = 'appeals'
    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    message_id = sqlalchemy.Column(sqlalchemy.BigInteger, unique=True, nullable=False)
    by_user = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)
