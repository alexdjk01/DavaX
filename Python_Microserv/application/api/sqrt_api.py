from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from application.db.session import SessionLocal
from application.models.db_model import MathOperation
from application.services.sqrt_service import calculate_sqrt
from application.utils.stream_writer import publish_to_stream

router = APIRouter()

class SqrtRequest(BaseModel):
    number: float

class SqrtResponse(BaseModel):
    result: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sqrt", response_model=SqrtResponse)
def compute_sqrt(request: SqrtRequest, db: Session = Depends(get_db)):
    publish_to_stream({
        "operation": "sqrt",
        "input": request.dict()
    })
    try:
        result = calculate_sqrt(request.number)

        operation = MathOperation(
            operation="sqrt",
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
            operation="sqrt",
            input_data=json.dumps({"number": request.number}),
            result=str(e),
            status="error"
        )
        db.add(operation)
        db.commit()
        return {"result": -1}
