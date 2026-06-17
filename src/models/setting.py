from sqlalchemy import Column, BigInteger, String
from src.models.base import Base


class DataDictionary(Base):
    __tablename__ = "data_dictionary"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(50), nullable=False, unique=True)
    value = Column(String(3000), nullable=True)
