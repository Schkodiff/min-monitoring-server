from typing import Any, List, Optional, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: Optional[str] = None
    data: Optional[T] = None

class SuccessAPIResponse(APIResponse):
    success: bool = True

class ErrorAPIResponse(APIResponse):
    success: bool = False

class ValidationErrorResponse(ErrorAPIResponse[List[str]]):
    pass