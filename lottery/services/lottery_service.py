from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session
from typing import List, Optional

from repositories.lottery_repository import LotteryRepository
from repositories.prize_repository import PrizeRepository
from repositories.ticket_repository import TicketRepository
from models.enums import LotteryStatus
from schemas.lottery import LotteryUpdate, LotteryResponse, LotteryCreate
from schemas.prize import PrizeCreate
from services.message_publisher import MessagePublisher


class LotteryService:
    def __init__(
        self,
        lotteries: LotteryRepository,
        prizes: PrizeRepository,
        tickets: TicketRepository,
        message_publisher: Optional[MessagePublisher] = None,
    ):
        self.lotteries = lotteries
        self.prizes = prizes
        self.tickets = tickets
        self.message_publisher = message_publisher

    def get_all_lotteries(self, session: Session) -> List[LotteryResponse]:
        lotteries = self.lotteries.list_all(session)
        return [LotteryResponse.from_orm(lottery) for lottery in lotteries]

    def get_lottery(self, session: Session, lottery_id: UUID) -> LotteryResponse:
        lottery = self.lotteries.get(session, lottery_id)
        if not lottery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Лотерея не найдена"
            )
        return LotteryResponse.model_validate(lottery)

    def get_lotteries_by_org(self, session: Session, org_id: UUID) -> List[LotteryResponse]:
        lotteries = self.lotteries.get_by_org_id(session, org_id)
        return [LotteryResponse.model_validate(lottery) for lottery in lotteries]

    def create_lottery(self, session: Session, lottery_create: LotteryCreate) -> LotteryResponse:
        existing = self.lotteries.get_by_name(session, lottery_create.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Лотерея с таким названием уже существует"
            )
        lottery_data = lottery_create.model_dump(exclude={'prizes'})
        new_lottery = self.lotteries.create_from_dict(session, lottery_data)

        if lottery_create.prizes:
            for prize_payload in lottery_create.prizes:
                data = prize_payload.model_dump()
                data["lottery_id"] = new_lottery.id
                self.prizes.create(session, PrizeCreate(**data))

        return LotteryResponse.model_validate(new_lottery)

    def update_lottery(self, session: Session, lottery_id: UUID, lottery_update: LotteryUpdate) -> LotteryResponse:
        lottery = self.lotteries.get(session, lottery_id)
        if not lottery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Лотерея не найдена"
            )
        
        previous_status = lottery.status
        updated_lottery = self.lotteries.update(session, lottery_id, lottery_update)
        if (
            lottery_update.status is not None
            and self.status_value(previous_status) != self.status_value(updated_lottery.status)
        ):
            self.publish_status_change_notifications(
                session,
                updated_lottery,
                previous_status,
            )
        return LotteryResponse.model_validate(updated_lottery)

    def publish_status_change_notifications(self, session: Session, lottery, previous_status) -> None:
        if not self.message_publisher:
            return

        notification_type = self.notification_type_for_status(lottery.status)
        if not notification_type:
            return

        tickets = self.tickets.get_by_lottery_id(session, lottery.id)
        receiver_ids = {ticket.user_id for ticket in tickets if ticket.user_id}
        if not receiver_ids:
            return

        previous = self.status_value(previous_status)
        current = self.status_value(lottery.status)
        for receiver_id in receiver_ids:
            self.message_publisher.publish_notification_background(
                {
                    "type": notification_type,
                    "message": f"Lottery '{lottery.name}' status changed from {previous} to {current}",
                    "receiver": str(receiver_id),
                    "lottery_id": str(lottery.id),
                }
            )

    @staticmethod
    def status_value(value) -> str:
        return value.value if isinstance(value, LotteryStatus) else str(value)

    @staticmethod
    def notification_type_for_status(lottery_status) -> Optional[str]:
        status_value = LotteryService.status_value(lottery_status)
        return {
            LotteryStatus.active.value: "lotteryStartsSoon",
            LotteryStatus.completed.value: "endOfLottery",
            LotteryStatus.inactive.value: "lotteryCancellation",
        }.get(status_value)

    def delete_lottery(self, session: Session, lottery_id: UUID) -> None:
        lottery = self.lotteries.get(session, lottery_id)
        if not lottery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Лотерея не найдена"
            )
        
        self.lotteries.delete(session, lottery_id)

    #set/get winner


def get_lottery_service():
    return LotteryService(
        LotteryRepository(),
        PrizeRepository(),
        TicketRepository(),
        MessagePublisher(),
    )

