from sqlalchemy.orm import Session

class BaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, model, id: int):
        return self.session.get(model, id)