from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from config.security import SecurityManager
from models.enums import UserRole

from schemas.notification import NotificationUpdate, NotificationResponse, NotificationCreate
from models.enums import NotificationType
from config.database import get_session
from services.notification_service import NotificationService, get_notification_service
from services.message_publisher import get_message_publisher
from responses.factory import Factory
from responses.API_response import SuccessAPIResponse


router = APIRouter()


@router.get("/", response_model=SuccessAPIResponse)
def get_all_notifications(session: Session = Depends(get_session), service: NotificationService = Depends(get_notification_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_all_notifications(session))


@router.get("/{notification_id}", response_model=SuccessAPIResponse)
def get_notification(notification_id: UUID, session: Session = Depends(get_session), service: NotificationService = Depends(get_notification_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_notification(session, notification_id))

@router.get("/", response_model=SuccessAPIResponse)
def get_notifications_by_type(notification_id: UUID, type: NotificationType, session: Session = Depends(get_session), service: NotificationService = Depends(get_notification_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_notifications_by_type(session, notification_id, type))

@router.post("/", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification_create: NotificationCreate, session: Session = Depends(get_session), service: NotificationService = Depends(get_notification_service), message_publisher = Depends(get_message_publisher), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    # Update service with message publisher
    service.message_publisher = message_publisher
    current_user_id, current_user_role = current_user
    return Factory.create_ok_reponse(data=service.create_notification(session, notification_create, current_user_role))


@router.patch("/{notification_id}", response_model=SuccessAPIResponse)
def update_notification(notification_id: UUID, notification_update: NotificationUpdate, session: Session = Depends(get_session), service: NotificationService = Depends(get_notification_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.update_notification(session, notification_id, notification_update))


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: UUID, session: Session = Depends(get_session), service: NotificationService = Depends(get_notification_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    service.delete_notification(session, notification_id)
    return None

