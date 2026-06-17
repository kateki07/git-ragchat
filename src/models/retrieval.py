from sqlalchemy import Column, BigInteger, String
from src.models.base import Base


class AiExtMessage(Base):
    __tablename__ = "ai_ext_message"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    run_id = Column(String(200), nullable=True)
    ext_context = Column(String(3000), nullable=True)
