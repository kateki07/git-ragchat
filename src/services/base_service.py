from sqlalchemy.orm import Session


class BaseService:
    """所有Service的基类，统一持有db会话"""

    def __init__(self, db: Session):
        self.db = db
