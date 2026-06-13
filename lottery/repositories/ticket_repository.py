from typing import Optional, List
from uuid import UUID

from schemas.ticket import TicketsBulkCreate, TicketsRangeCreate
from .base_repository import BaseRepository
from sqlmodel import Session, select

from models.ticket import Ticket
from models.enums import TicketStatus
from models.prize import Prize


class TicketRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ticket)

    def get_by_lottery_id(self, session: Session, lottery_id: UUID) -> List[Ticket]:
        return session.query(Ticket).filter(Ticket.lottery_id == lottery_id).all()

    def get_by_serial_number(self, session: Session, serial_number: str) -> Optional[Ticket]:
        return session.query(Ticket).filter(Ticket.serial_number == serial_number).first()
    
    def get_by_user_id(self, session: Session, user_id: UUID) -> List[Ticket]:
        return session.query(Ticket).filter(Ticket.user_id == user_id).all()

    def get_user_by_ticket(self, session: Session, ticket_id: UUID) -> Optional[UUID]:
        ticket = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        return ticket.user_id if ticket else None

    def get_winners(self, session: Session, lottery_id: Optional[UUID] = None) -> List[Ticket]:
        query = session.query(Ticket).filter(Ticket.is_winner == True)
        if lottery_id:
            query = query.filter(Ticket.lottery_id == lottery_id)
        return query.all()

    def get_prize(self, session: Session, prize_id: UUID) -> Optional[Prize]:
        return session.get(Prize, prize_id)

    def set_winner(
        self,
        session: Session,
        ticket: Ticket,
        is_winner: bool = True,
        prize_id: Optional[UUID] = None,
    ) -> Ticket:
        ticket.is_winner = is_winner
        if prize_id is not None:
            for p in session.query(Prize).filter(Prize.ticket_id == ticket.id).all():
                if p.id != prize_id:
                    p.ticket_id = None
                    session.add(p)
            prize = session.get(Prize, prize_id)
            if prize is not None:
                prize.ticket_id = ticket.id
                session.add(prize)
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket

    def change_status(self, session: Session, ticket: Ticket, status: TicketStatus) -> Optional[Ticket]:
        ticket.status = status.value
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket

    def link_user_tickets(self, session: Session, tickets: List[Ticket], user_id: UUID) -> List[Ticket]:
        for ticket in tickets:
            ticket.user_id = user_id
            ticket.status = TicketStatus.booked
            session.add(ticket)
        session.commit()
        for ticket in tickets:
            session.refresh(ticket)
        return tickets

    def bulk_create(self, session: Session, ticket_bulk_create: TicketsBulkCreate) -> List[Ticket]:
        batch_size = ticket_bulk_create.number
        new_tickets = [Ticket(lottery_id= ticket_bulk_create.lottery_id, price = ticket_bulk_create.price, serial_number = f"lottery_{ticket_bulk_create.lottery_id}_{i}") for i in range(batch_size)]
        for i in range(0, len(new_tickets), batch_size):
            batch = new_tickets[i:i + batch_size]
            session.bulk_save_objects(batch)
            session.flush()  # Optional: apply without full commit
        session.commit()
        return new_tickets

    def range_create(self, session: Session, ticket_range_create: TicketsRangeCreate) -> List[Ticket]:
        numero1 = ticket_range_create.serial_number1
        numero2 = ticket_range_create.serial_number2
        if numero1 > numero2:
            temp = numero2
            numero2 = numero1
            numero1 = temp
        batch_size = numero2 - numero1
        new_tickets = [Ticket(lottery_id= ticket_range_create.lottery_id, price = ticket_range_create.price, serial_number = f"lottery_{ticket_range_create.lottery_id}_{i}") for i in range(numero1, numero2+1)]
        for i in range(0, len(new_tickets), batch_size):
            batch = new_tickets[i:i + batch_size]
            session.bulk_save_objects(batch)
            session.flush()  # Optional: apply without full commit
        session.commit()
        return new_tickets

    #session.bulk_save_objects(objects)
    #price, range of ticket.serial_numbers