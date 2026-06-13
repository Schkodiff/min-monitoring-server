from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List
from models.enums import UserRole

from repositories.organizer_repository import OrganizerRepository
from schemas.organizer import OrganizerUpdate, OrganizerResponse, OrganizerCreate


class OrganizerService:
    def __init__(self, organizers: OrganizerRepository):
        self.organizers = organizers

    def get_all_organizers(self, session: Session) -> List[OrganizerResponse]:
        organizers = self.organizers.list_all(session)
        return [OrganizerResponse.model_validate(organizer) for organizer in organizers]

    def get_organizer(self, session: Session, organizer_id: UUID) -> OrganizerResponse:
        organizer = self.organizers.get(session, organizer_id)
        if not organizer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организатор не найден"
            )
        return OrganizerResponse.model_validate(organizer)

    def create_organizer(self, session: Session, organizer_create: OrganizerCreate, current_user_role: UserRole) -> OrganizerResponse:
        if current_user_role != UserRole.admin or current_user_role != UserRole.mod:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="At least moderator privileges required"
            )
        existing = self.organizers.get_by_email(session, organizer_create.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким email уже существует"
            )
        
        existing = self.organizers.get_by_phone(session, organizer_create.phone)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким телефоном уже существует"
            )
        
        existing = self.organizers.get_by_inn(session, organizer_create.inn)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким ИНН уже существует"
            )
        
        existing = self.organizers.get_by_ogrn(session, organizer_create.ogrn)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким ОГРН уже существует"
            )
        
        new_organizer = self.organizers.create(session, organizer_create)
        return OrganizerResponse.model_validate(new_organizer)

    def update_organizer(self, session: Session, organizer_id: UUID, organizer_update: OrganizerUpdate) -> OrganizerResponse:
        organizer = self.organizers.get(session, organizer_id)
        if not organizer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организатор не найден"
            )
        
        if organizer_update.email:
            existing = self.organizers.get_by_email(session, organizer_update.email)
            if existing and existing.id != organizer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Организатор с таким email уже существует"
                )
        
        if organizer_update.phone:
            existing = self.organizers.get_by_phone(session, organizer_update.phone)
            if existing and existing.id != organizer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Организатор с таким телефоном уже существует"
                )
        
        updated_organizer = self.organizers.update(session, organizer_id, organizer_update)
        return OrganizerResponse.model_validate(updated_organizer)

    def delete_organizer(self, session: Session, organizer_id: UUID) -> None:
        organizer = self.organizers.get(session, organizer_id)
        if not organizer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организатор не найден"
            )
        
        self.organizers.delete(session, organizer_id)


def get_organizer_service():
    return OrganizerService(OrganizerRepository())

