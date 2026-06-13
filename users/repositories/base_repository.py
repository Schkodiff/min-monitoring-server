from typing import Optional, List
from uuid import UUID
from sqlmodel import select, Session
from pydantic import BaseModel
from models.basemodel import EntityBaseModel
from config.database import get_session


class BaseRepository:
    def __init__(self, model: EntityBaseModel) -> None:
        self.model = model

    def get(self, session: Session, id: UUID) -> Optional[EntityBaseModel]:
        return session.query(self.model).filter(self.model.id == id).first()

    def list_all(self, session: Session) -> List[EntityBaseModel]:
        return session.query(self.model).all()

    def create(self, session: Session, obj: BaseModel) -> EntityBaseModel:
        data = obj.model_dump()
        new_obj = self.model(**data)
        session.add(new_obj)
        session.commit()
        session.refresh(new_obj)
        return new_obj

    def update(self, session: Session, id: UUID, obj: BaseModel) -> EntityBaseModel:
        entity_obj = session.query(self.model).filter(self.model.id == id).first()
        data = obj.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(entity_obj, field, value)
        session.add(entity_obj)
        session.commit()
        session.refresh(entity_obj)
        return entity_obj

    def delete(self, session: Session, id: UUID) -> None:
        obj = session.query(self.model).filter(self.model.id == id).first()
        if obj:
            session.delete(obj)
            session.commit()