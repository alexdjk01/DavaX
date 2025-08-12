from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from application.db.session import SessionLocal
from application.models.db_model import MathOperation
from application.services.log_service import calculate_log
from application.utils.stream_writer import publish_to_stream

router = APIRouter()

class LogRequest(BaseModel):
    number: float

class LogResponse(BaseModel):
    result: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/log", response_model=LogResponse)
def compute_log(request: LogRequest, db: Session = Depends(get_db)):
    publish_to_stream({
        "operation": "log",
        "input": request.dict()
    })
    try:
        result = calculate_log(request.number)
        operation = MathOperation(
            operation="log",
            input_data=json.dumps({"number": request.number}),
            result=str(result),
            status="success"
        )
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return {"result": result}
    except Exception as e:
        operation = MathOperation(
            operation="log",
            input_data=json.dumps({"number": request.number}),
            result=str(e),
            status="error"
        )
        db.add(operation)
        db.commit()
        return {"result": -1}
