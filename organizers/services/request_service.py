from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from models.enums import RequestStatus, UserRole

from config.messaging import NULL_LOTTERY_ID
from repositories.organizer_repository import OrganizerRepository
from repositories.request_repository import RequestRepository
from schemas.request import RequestStatusChange, RequestUpdate, RequestResponse, RequestCreate
from services.message_publisher import MessagePublisher


class RequestService:
    def __init__(
        self,
        requests: RequestRepository,
        message_publisher: Optional[MessagePublisher] = None,
        organizers: Optional[OrganizerRepository] = None,
    ):
        self.requests = requests
        self.message_publisher = message_publisher
        self.organizers = organizers or OrganizerRepository()

    def get_all_requests(self, session: Session) -> List[RequestResponse]:
        requests = self.requests.list_all(session)
        return [RequestResponse.model_validate(request) for request in requests]
    
    def get_by_user(self, session: Session, user_id: UUID) -> List[RequestResponse]:
        requests = self.requests.get_by_user_id(session, user_id)
        return [RequestResponse.model_validate(request) for request in requests]

    def get_request(self, session: Session, request_id: UUID) -> RequestResponse:
        request = self.requests.get(session, request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организатор не найден"
            )
        return RequestResponse.model_validate(request)

    def create_request(
        self,
        session: Session,
        request_create: RequestCreate,
        current_user_id: UUID,
        current_user_role: UserRole,
    ) -> RequestResponse:
        if current_user_role == UserRole.organizer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organizer already exists for this account"
            )
        existing = self.requests.get_by_email(session, request_create.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким email уже существует"
            )
        
        existing = self.requests.get_by_phone(session, request_create.phone)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким телефоном уже существует"
            )
        
        existing = self.requests.get_by_inn(session, request_create.inn)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким ИНН уже существует"
            )
        
        existing = self.requests.get_by_ogrn(session, request_create.ogrn)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Организатор с таким ОГРН уже существует"
            )
        
        request_data = request_create.model_dump()
        request_data["user_id"] = current_user_id
        new_request = self.requests.create_from_dict(session, request_data)
        return RequestResponse.model_validate(new_request)

    def update_request(self, session: Session, request_id: UUID, request_update: RequestUpdate) -> RequestResponse:
        request = self.requests.get(session, request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организатор не найден"
            )
        
        if request_update.email:
            existing = self.requests.get_by_email(session, request_update.email)
            if existing and existing.id != request_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Организатор с таким email уже существует"
                )
        
        if request_update.phone:
            existing = self.requests.get_by_phone(session, request_update.phone)
            if existing and existing.id != request_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Организатор с таким телефоном уже существует"
                )
        
        updated_request = self.requests.update(session, request_id, request_update)
        return RequestResponse.model_validate(updated_request)

    def _raise_if_organizer_exists(self, session: Session, request) -> None:
        duplicate_checks = (
            (self.organizers.get_by_email(session, request.email), "email"),
            (self.organizers.get_by_phone(session, request.phone), "phone"),
            (self.organizers.get_by_address(session, request.address), "address"),
            (self.organizers.get_by_inn(session, request.inn), "INN"),
            (self.organizers.get_by_ogrn(session, request.ogrn), "OGRN"),
        )
        for existing, field_name in duplicate_checks:
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Organizer with this {field_name} already exists",
                )

    def _approve_request(self, session: Session, request, current_user_id: UUID):
        self._raise_if_organizer_exists(session, request)

        organizer_data = {
            "name": request.name,
            "inn": request.inn,
            "ogrn": request.ogrn,
            "phone": request.phone,
            "address": request.address,
            "logo": request.logo,
            "email": request.email,
        }

        request.status = RequestStatus.accepted
        request.poc_id = current_user_id
        request.rejection_reason = None

        session.add(request)
        try:
            self.organizers.create_from_dict_with_owner(
                session,
                organizer_data,
                request.user_id,
            )
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organizer with matching unique fields already exists",
            )
        session.refresh(request)
        return request

    def change_request_status(
        self,
        session: Session,
        request_id: UUID,
        status_change: RequestStatusChange,
        current_user_id: UUID,
        current_user_role: UserRole,
    ) -> RequestResponse:
        if current_user_role not in (UserRole.admin, UserRole.mod):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="At least moderator privileges required"
            )

        request = self.requests.get(session, request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )
        if status_change.status == request.status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already has this status"
            )

        if status_change.status == RequestStatus.accepted:
            updated_request = self._approve_request(session, request, current_user_id)
        else:
            updated_request = self.requests.change_status(
                session,
                request,
                status_change.status,
                current_user_id,
                status_change.rejection_reason,
            )
        if self.message_publisher and status_change.status in (
            RequestStatus.accepted,
            RequestStatus.rejected,
        ):
            notification_type = (
                "orgRegReqApproval"
                if status_change.status == RequestStatus.accepted
                else "orgRegReqRejection"
            )
            message = (
                f"Organizer request '{updated_request.name}' has been approved"
                if status_change.status == RequestStatus.accepted
                else f"Organizer request '{updated_request.name}' has been rejected"
            )
            self.message_publisher.publish_notification_background(
                {
                    "type": notification_type,
                    "message": message,
                    "receiver": str(updated_request.user_id),
                    "lottery_id": NULL_LOTTERY_ID,
                    "author": str(current_user_id),
                }
            )
        return RequestResponse.model_validate(updated_request)

    def delete_request(self, session: Session, request_id: UUID) -> None:
        request = self.requests.get(session, request_id)
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Организатор не найден"
            )
        
        self.requests.delete(session, request_id)


def get_request_service():
    return RequestService(RequestRepository(), MessagePublisher(), OrganizerRepository())
