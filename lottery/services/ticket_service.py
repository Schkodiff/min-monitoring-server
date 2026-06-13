from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional

from repositories.ticket_repository import TicketRepository
from schemas.ticket import TicketStatusChange, TicketUpdate, TicketResponse, TicketCreate, TicketUserIdResponse, TicketsBulkCreate, TicketsRangeCreate
from models.enums import TicketStatus
from models.ticket import Ticket
from services.message_publisher import MessagePublisher


class TicketService:
    def __init__(self, tickets: TicketRepository, message_publisher: Optional[MessagePublisher] = None):
        self.tickets = tickets
        self.message_publisher = message_publisher

    def get_all_tickets(self, session: Session) -> List[TicketResponse]:
        tickets = self.tickets.list_all(session)
        return [TicketResponse.model_validate(ticket) for ticket in tickets]

    def get_ticket(self, session: Session, ticket_id: UUID) -> TicketResponse:
        ticket = self.tickets.get(session, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Билет не найден"
            )
        return TicketResponse.model_validate(ticket)

    def get_tickets_by_lottery(self, session: Session, lottery_id: UUID) -> List[TicketResponse]:
        tickets = self.tickets.get_by_lottery_id(session, lottery_id)
        return [TicketResponse.model_validate(ticket) for ticket in tickets]

    def get_tickets_by_user(self, session: Session, user_id: UUID) -> List[TicketResponse]:
        tickets = self.tickets.get_by_user_id(session, user_id)
        return [TicketResponse.model_validate(ticket) for ticket in tickets]
    
    def get_user_by_ticket(self, session: Session, ticket_id: UUID) -> Optional[UUID]:
        user_id = self.tickets.get_user_by_ticket(session, ticket_id)
        return TicketUserIdResponse(user_id=user_id) if user_id else None

    def get_winners(self, session: Session, lottery_id: Optional[UUID] = None) -> List[TicketResponse]:
        tickets = self.tickets.get_winners(session, lottery_id)
        return [TicketResponse.model_validate(ticket) for ticket in tickets]

    def create_ticket(self, session: Session, ticket_create: TicketCreate) -> TicketResponse:
        existing = self.tickets.get_by_serial_number(session, ticket_create.serial_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Билет с таким серийным номером уже существует"
            )
        
        new_ticket = self.tickets.create(session, ticket_create)
        return TicketResponse.model_validate(new_ticket)

    def link_user_tickets(
        self, session: Session, lottery_id: UUID, ticket_ids: List[UUID], user_id: UUID
    ) -> List[TicketResponse]:
        unique_ids = list(dict.fromkeys(ticket_ids))
        if not unique_ids:
            return []
        tickets: List[Ticket] = []
        for ticket_id in unique_ids:
            ticket = self.tickets.get(session, ticket_id)
            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Билет не найден"
                )
            if ticket.lottery_id != lottery_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Билет не относится к указанной лотерее"
                )
            if ticket.status != TicketStatus.vacant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Билет уже куплен другим пользователем"
                )
            tickets.append(ticket)
        updated = self.tickets.link_user_tickets(session, tickets, user_id)
        return [TicketResponse.model_validate(t) for t in updated]

    def update_ticket(self, session: Session, ticket_id: UUID, ticket_update: TicketUpdate) -> TicketResponse:
        ticket = self.tickets.get(session, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Билет не найден"
            )
        
        if ticket_update.serial_number:
            existing = self.tickets.get_by_serial_number(session, ticket_update.serial_number)
            if existing and existing.id != ticket_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Билет с таким серийным номером уже существует"
                )
        
        updated_ticket = self.tickets.update(session, ticket_id, ticket_update)
        return TicketResponse.model_validate(updated_ticket)

    def change_ticket_status(self, session: Session, ticket_id: UUID, ticket_status_change: TicketStatusChange) -> TicketResponse:
        ticket = self.tickets.get(session, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Билет не найден"
            )
        
        if ticket_status_change.status == ticket.status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Билет уже имеет такой статуст"
            )
        
        previous_status = ticket.status
        updated_ticket = self.tickets.change_status(session, ticket, ticket_status_change.status)
        previous_status_value = previous_status.value if isinstance(previous_status, TicketStatus) else previous_status

        if self.message_publisher and updated_ticket.user_id:
            if ticket_status_change.status == TicketStatus.paid:
                 self.message_publisher.publish_notification_background(
                    {
                        "type": "ticketBuyApproval",
                        "message": f"Ticket {updated_ticket.serial_number} purchase has been approved",
                        "receiver": str(updated_ticket.user_id),
                        "lottery_id": str(updated_ticket.lottery_id),
                    }
                )
            elif (
                previous_status_value == TicketStatus.booked.value
                and ticket_status_change.status == TicketStatus.vacant
            ):
                self.message_publisher.publish_notification_background(
                    {
                        "type": "ticketBuyRejection",
                        "message": f"Ticket {updated_ticket.serial_number} purchase has been rejected",
                        "receiver": str(updated_ticket.user_id),
                        "lottery_id": str(updated_ticket.lottery_id),
                    }
                )
        return TicketResponse.model_validate(updated_ticket)

    def set_winner(
        self,
        session: Session,
        ticket_id: UUID,
        is_winner: bool = True,
        prize_id: Optional[UUID] = None,
    ) -> TicketResponse:
        ticket = self.tickets.get(session, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Билет не найден"
            )
        if prize_id is not None:
            prize = self.tickets.get_prize(session, prize_id)
            if not prize:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Приз не найден"
                )
            if prize.lottery_id != ticket.lottery_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Приз не относится к лотерее этого билета"
                )
        updated_ticket = self.tickets.set_winner(session, ticket, is_winner, prize_id)
        if self.message_publisher and is_winner and updated_ticket.user_id:
            self.message_publisher.publish_notification_background(
                {
                    "type": "win",
                    "message": f"Ticket {updated_ticket.serial_number} won a prize",
                    "receiver": str(updated_ticket.user_id),
                    "lottery_id": str(updated_ticket.lottery_id),
                }
            )
        return TicketResponse.model_validate(updated_ticket)

    def delete_ticket(self, session: Session, ticket_id: UUID) -> None:
        ticket = self.tickets.get(session, ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Билет не найден"
            )
        
        self.tickets.delete(session, ticket_id)

    def bulk_create_tickets(self, session: Session, ticket_bulk_create: TicketsBulkCreate) -> List[TicketResponse]:
        new_tickets = self.tickets.bulk_create(session, ticket_bulk_create)
        return [TicketResponse.model_validate(ticket) for ticket in new_tickets]

    def range_create_tickets(self, session: Session, ticket_range_create: TicketsRangeCreate) -> List[TicketResponse]:
        new_tickets = self.tickets.range_create(session, ticket_range_create)
        return [TicketResponse.model_validate(ticket) for ticket in new_tickets]


def get_ticket_service():
    return TicketService(TicketRepository(), MessagePublisher())
