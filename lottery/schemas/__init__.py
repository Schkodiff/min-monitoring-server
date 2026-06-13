from .lottery import LotteryResponse, LotteryCreate, LotteryUpdate
from .prize import PrizeResponse, PrizeCreate, PrizeUpdate
from .ticket import TicketResponse, TicketCreate, TicketUpdate

LotteryResponse.model_rebuild()
PrizeResponse.model_rebuild()
TicketResponse.model_rebuild()
