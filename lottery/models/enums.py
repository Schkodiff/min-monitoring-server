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