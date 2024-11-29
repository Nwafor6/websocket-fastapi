""" models.py """

from uuid import uuid4
from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    """
    User model
    """

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=str(uuid4))
    password = Column(String)
    email = Column(String, unique=True, index=True)
