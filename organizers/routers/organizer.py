from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from config.security import SecurityManager
from models.enums import UserRole

from schemas.organizer import OrganizerUpdate, OrganizerResponse, OrganizerCreate
from config.database import get_session
from services.organizer_service import OrganizerService, get_organizer_service
from responses.factory import Factory
from responses.API_response import SuccessAPIResponse


router = APIRouter()


@router.get("/", response_model=SuccessAPIResponse)
def get_all_organizers(session: Session = Depends(get_session), service: OrganizerService = Depends(get_organizer_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_all_organizers(session))


@router.get("/{organizer_id}", response_model=SuccessAPIResponse)
def get_organizer(organizer_id: UUID, session: Session = Depends(get_session), service: OrganizerService = Depends(get_organizer_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_organizer(session, organizer_id))


@router.post("/", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_organizer(organizer_create: OrganizerCreate, session: Session = Depends(get_session), service: OrganizerService = Depends(get_organizer_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    current_user_id, current_user_role = current_user
    return Factory.create_ok_reponse(data=service.create_organizer(session, organizer_create, current_user_role))


@router.patch("/{organizer_id}", response_model=SuccessAPIResponse)
def update_organizer(organizer_id: UUID, organizer_update: OrganizerUpdate, session: Session = Depends(get_session), service: OrganizerService = Depends(get_organizer_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.update_organizer(session, organizer_id, organizer_update))


@router.delete("/{organizer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organizer(organizer_id: UUID, session: Session = Depends(get_session), service: OrganizerService = Depends(get_organizer_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    service.delete_organizer(session, organizer_id)
    return None

