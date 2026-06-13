from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
import hashlib
from typing import Optional

from config.messaging import NULL_LOTTERY_ID
from repositories.user_repository import UserRepository
from schemas.user import UserIdByTelegramIdResponse, UserLinkTelegramResponse, UserUpdate, UserResponse, UserRole, UserChangeRole, UserTelegramCodeResponse, UserTelegramIdResponse, UserLinkTelegram
from services.message_publisher import MessagePublisher


class UserService:
    def __init__(self, users: UserRepository, message_publisher: Optional[MessagePublisher] = None):
        self.users = users
        self.message_publisher = message_publisher

    def get_all_users(self, session: Session) -> list[UserResponse]:
        users = self.users.list_all(session)
        return [UserResponse.from_orm(user) for user in users]

    def get_user(self, session: Session, user_id: UUID) -> UserResponse:
        user = self.users.get(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return UserResponse.from_orm(user)   

    def update_user(self, session: Session, user_id: UUID, user_update: UserUpdate, current_user_id: UUID) -> UserResponse:
        if current_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя изменить чужой профиль"
            )
        
        user = self.users.get(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        update_dict = user_update.model_dump(exclude_unset=True, exclude={'telegram_id'})
        updated_user = self.users.update(session, user_id, UserUpdate(**update_dict))
        return UserResponse.from_orm(updated_user)

    def delete_user(self, session: Session, user_id: UUID, current_user_id: UUID) -> None:
    #нужно ли вообще
        current_user = self.users.get(session, current_user_id)
        if not current_user or current_user.role not in (UserRole.admin, UserRole.mod):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        user = self.users.get(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        self.users.delete(session, user_id)
        if self.message_publisher:
            self.message_publisher.publish_notification_background(
                {
                    "type": "accountBan",
                    "message": "Account has been blocked",
                    "receiver": str(user_id),
                    "lottery_id": NULL_LOTTERY_ID,
                    "author": str(current_user_id),
                }
            )
    
    def change_role(self, session: Session, user_id: UUID, user_change_role: UserChangeRole, current_user_role: UserRole) -> UserResponse:
        if current_user_role != UserRole.admin or current_user_role != UserRole.mod:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя изменить роль без административных прав"
            )
        user = self.users.get(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        updated_user = self.users.change_role(session, user_id, user_change_role.role)
        return UserResponse.from_orm(updated_user)

    def get_user_by_telegram_id(self, session: Session, telegram_id: UUID) -> UserResponse:
        user = self.users.get_by_telegram_id(session, telegram_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return UserResponse.from_orm(user)

    def get_telegram_id(self, session: Session, current_user_id: UUID) -> UserTelegramIdResponse:
        user = self.users.get(session, current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        if not user.telegram_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Телеграм ID не найден"
            )
        return UserTelegramIdResponse(telegram_id=user.telegram_id)

    def get_user_id_by_telegram_id(self, session: Session, telegram_id: int) -> UserIdByTelegramIdResponse:
        user = self.users.get_by_telegram_id(session, telegram_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return UserIdByTelegramIdResponse(user_id=user.id)

    def generate_telegram_code(self, session: Session, current_user_id: UUID) -> UserTelegramCodeResponse:
        user = self.users.get(session, current_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        concat = str(current_user_id).encode("utf-8") + str(user.password).encode("utf-8")
        code = hashlib.sha3_256(concat).hexdigest()
        self.users.set_telegram_code(session, user, code)
        return UserTelegramCodeResponse(telegram_code=code)

    def link_telegram_id(self, session: Session, telegram_id: int, telegram_code: str) -> UserLinkTelegramResponse:
        user = self.users.get_by_telegram_code(session, telegram_code)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        if user.telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Телеграм ID уже связан с другим пользователем"
            )
        self.users.link_telegram_id(session, user, telegram_id)
        return UserLinkTelegramResponse(telegram_id=telegram_id, user_id=user.id)


def get_user_service():
    return UserService(UserRepository(), MessagePublisher())
