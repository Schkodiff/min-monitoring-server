from enum import Enum


class UserRole(str, Enum):
    organizer = "organizer"
    participant = "participant"
    admin = "admin"
    mod = "moderator"

class TicketStatus(str, Enum):
    booked = "booked"
    paid = "paid"
    vacant = "vacant"

class LotteryStatus(str, Enum):
    active = "active"
    completed = "completed"
    inactive = "inactive"
    #cancelled?

class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class NotificationType(str, Enum):
# 1. Победа, событие: конец розыгрыша при учете того, что билет победный
# 2. Конец розыгрыша, событие: конец розыгрыша при учете того, что билет не победный
# 3. Скорое начало розыгрыша, событие: розыгрыш начнется завтра
# 4. Одобрение покупки билета, событие: организатор одобрил покупку билета
# 5. Одобрение заявки на создание организации, событие: админ одобрил заявку организации
# 6. Отклонение заявки на создание организации, событие: админ не одобрил заявку организации
# 7. Отклонение покупки билета, событие: организатор не одобрил покупку билета
# 8. Бан аккаунта, событие: аккаунт заблокирован
# 9. Отмена розыгрыша, событие: розыгрыш был отменен
# 10. Кастомные сообщения от организатора, событие: организатор запостил что-то
    win = "win"
    endOfLottery = "endOfLottery"
    lotteryStartsSoon = "lotteryStartsSoon"
    ticketBuyApproval = "ticketBuyApproval"
    orgRegReqApproval = "orgRegReqApproval"
    ticketBuyRejection = "ticketBuyRejection"
    orgRegReqRejection = "orgRegReqRejection"
    accountBan = "accountBan"
    lotteryCancellation = "lotteryCancellation"
    postByOrg = "postByOrg"