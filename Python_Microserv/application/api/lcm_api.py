from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from application.db.session import SessionLocal
from application.models.db_model import MathOperation
from application.services.lcm_service import calculate_lcm
from application.utils.stream_writer import publish_to_stream

router = APIRouter()

class LCMRequest(BaseModel):
    a: int
    b: int

class LCMResponse(BaseModel):
    result: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/lcm", response_model=LCMResponse)
def compute_lcm(request: LCMRequest, db: Session = Depends(get_db)):
    publish_to_stream({
        "operation": "lcm",
        "input": request.dict()
    })
    try:
        result = calculate_lcm(request.a, request.b)
        operation = MathOperation(
            operation="lcm",
            input_data=json.dumps({"a": request.a, "b": request.b}),
            result=str(result),
            status="success"
        )
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return {"result": result}
    except Exception as e:
        operation = MathOperation(
            operation="lcm",
            input_data=json.dumps({"a": request.a, "b": request.b}),
            result=str(e),
            status="error"
        )
        db.add(operation)
        db.commit()
        return {"result": -1}
