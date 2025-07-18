from pydantic import BaseModel
from typing import Union, Literal, Any
from datetime import datetime


class OperationRequest(BaseModel):
    operation: Literal["pow", "factorial", "fibonacci"]
    input_data: Any  # dict or int, depending on the operation


class OperationResponse(BaseModel):
    id: int
    operation: str
    input_data: Any
    result: str
    status: str
    created_at: datetime


class Config:
    orm_mode = True  # return SQLAlchemy objects
