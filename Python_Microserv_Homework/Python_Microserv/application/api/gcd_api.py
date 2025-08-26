from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from application.db.session import SessionLocal
from application.models.db_model import MathOperation
from application.services.gcd_service import calculate_gcd
from application.utils.stream_writer import publish_to_stream

router = APIRouter()

class GCDRequest(BaseModel):
    a: int
    b: int

class GCDResponse(BaseModel):
    result: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/gcd", response_model=GCDResponse)
def compute_gcd(request: GCDRequest, db: Session = Depends(get_db)):
    publish_to_stream({
        "operation": "gcd",
        "input": request.dict()
    })
    try:
        result = calculate_gcd(request.a, request.b)
        operation = MathOperation(
            operation="gcd",
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
            operation="gcd",
            input_data=json.dumps({"a": request.a, "b": request.b}),
            result=str(e),
            status="error"
        )
        db.add(operation)
        db.commit()
        return {"result": -1}
