from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional

from schemas.ticket import (
    TicketStatusChange,
    TicketUpdate,
    TicketResponse,
    TicketCreate,
    TicketsBulkCreate,
    TicketsRangeCreate,
    BuyTicketsRequest,
    TicketPrizeConnect,
)
from config.database import get_session
from services.ticket_service import TicketService, get_ticket_service
from responses.factory import Factory
from responses.API_response import SuccessAPIResponse
from config.security import SecurityManager
from models.enums import UserRole

router = APIRouter()


@router.get("/", response_model=SuccessAPIResponse)
def get_all_tickets(session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_all_tickets(session))


@router.get("/{ticket_id}", response_model=SuccessAPIResponse)
def get_ticket(ticket_id: UUID, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_ticket(session, ticket_id))


@router.get("/lottery/{lottery_id}", response_model=SuccessAPIResponse)
def get_tickets_by_lottery(lottery_id: UUID, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_tickets_by_lottery(session, lottery_id))


@router.get("/user/{user_id}", response_model=SuccessAPIResponse)
def get_tickets_by_user(user_id: UUID, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_tickets_by_user(session, user_id))

@router.get("/{ticket_id}/user", response_model=SuccessAPIResponse)
def get_user_by_ticket(ticket_id: UUID, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_user_by_ticket(session, ticket_id))

@router.get("/winners/{lottery_id}", response_model=SuccessAPIResponse)
def get_winners_by_lottery(lottery_id: UUID, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_winners(session, lottery_id))


@router.get("/winners/", response_model=SuccessAPIResponse)
def get_all_winners(session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.get_winners(session))


@router.post("/", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_create: TicketCreate, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.create_ticket(session, ticket_create))

@router.post("/create-tickets", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_tickets(ticket_bulk_create: TicketsBulkCreate, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.bulk_create_tickets(session, ticket_bulk_create))

@router.post("/create-tickets-range", response_model=SuccessAPIResponse, status_code=status.HTTP_201_CREATED)
def create_tickets_range(ticket_range_create: TicketsRangeCreate, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.range_create_tickets(session, ticket_range_create))

@router.patch("/{ticket_id}", response_model=SuccessAPIResponse)
def update_ticket(ticket_id: UUID, ticket_update: TicketUpdate, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.update_ticket(session, ticket_id, ticket_update))

@router.patch("/{ticket_id}/change-status", response_model=SuccessAPIResponse)
def update_ticket(ticket_id: UUID, ticket_status_change: TicketStatusChange, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    return Factory.create_ok_reponse(data=service.change_ticket_status(session, ticket_id, ticket_status_change))

@router.patch("/{ticket_id}/set-winner", response_model=SuccessAPIResponse)
def set_winner(
    ticket_id: UUID,
    body: TicketPrizeConnect,
    session: Session = Depends(get_session),
    service: TicketService = Depends(get_ticket_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    return Factory.create_ok_reponse(data=service.set_winner(session, ticket_id, True, body.prize_id))

@router.patch("/{lottery_id}/buy_tickets", response_model=SuccessAPIResponse)
def buy_tickets(
    lottery_id: UUID,
    body: BuyTicketsRequest,
    session: Session = Depends(get_session),
    service: TicketService = Depends(get_ticket_service),
    current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token),
):
    return Factory.create_ok_reponse(
        data=service.link_user_tickets(session, lottery_id, body.ticket_ids, body.user_id)
    )

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: UUID, session: Session = Depends(get_session), service: TicketService = Depends(get_ticket_service), current_user: tuple[UUID, UserRole] = Depends(SecurityManager.decode_access_token)):
    service.delete_ticket(session, ticket_id)
    return None

