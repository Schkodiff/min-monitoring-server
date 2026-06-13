from typing import TypeVar, Optional
from responses.API_response import SuccessAPIResponse, ErrorAPIResponse

T = TypeVar('T')

class Factory:
    @classmethod
    def create_ok_reponse(cls, data: Optional[T] = None, message: str = "") -> SuccessAPIResponse[T]:
        return SuccessAPIResponse[T](message=message, data=data)
    
    @classmethod
    def create_not_found_reponse(cls, data: Optional[T] = None, message: str = ""):
        return ErrorAPIResponse(message='Не найдено', data=[message])