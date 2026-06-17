from sqlalchemy import Column, String
from src.models.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False)
