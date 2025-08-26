from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from application.db.session import SessionLocal
from application.models.db_model import MathOperation
from application.services.pow_service import calculate_power
from application.utils.stream_writer import publish_to_stream

router = APIRouter()


class PowRequest(BaseModel):
    base: float
    exponent: float


class PowResponse(BaseModel):
    result: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/pow", response_model=PowResponse)
def compute_pow(request: PowRequest, db: Session = Depends(get_db)):
    publish_to_stream({
        "operation": "pow",
        "input": request.dict()
    })
    try:
        result = calculate_power(request.base, request.exponent)
        operation = MathOperation(
            operation="pow",
            input_data=json.dumps({"base": request.base, "exponent": request.exponent}),
            result=str(result),
            status="success",
        )
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return {"result": result}
    except Exception as e:
        operation = MathOperation(
            operation="pow",
            input_data=json.dumps({"base": request.base, "exponent": request.exponent}),
            result=str(e),
            status="error",
        )
        db.add(operation)
        db.commit()
        return {"result": f"Error: {str(e)}"}
