import sqlalchemy
from .database import SqlAlchemyBase


class Thread(SqlAlchemyBase):
    __tablename__ = 'threads'
    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    message_thread_id = sqlalchemy.Column(sqlalchemy.BigInteger, unique=True, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    by_user = sqlalchemy.Column(sqlalchemy.BigInteger, nullable=False)
    is_open = sqlalchemy.Column(sqlalchemy.Boolean, default=True)