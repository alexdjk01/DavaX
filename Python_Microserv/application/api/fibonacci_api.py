from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from application.services.fibonacci_service import calculate_fibonacci
from application.db.session import SessionLocal
from application.models.db_model import MathOperation
import json

router = APIRouter()


class FibonacciRequest(BaseModel):
    number: int


class FibonacciResponse(BaseModel):
    result: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/fibonacci", response_model=FibonacciResponse)
def compute_fibonacci(request: FibonacciRequest, db: Session = Depends(get_db)):
    try:
        result = calculate_fibonacci(request.number)
        operation = MathOperation(
            operation="fibonacci",
            input_data=json.dumps({"number": request.number}),
            result=str(result),
            status="success",
        )
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return {"result": result}
    except Exception as e:
        operation = MathOperation(
            operation="fibonacci",
            input_data=json.dumps({"number": request.number}),
            result=str(e),
            status="error",
        )
        db.add(operation)
        db.commit()
        return {"result": f"Error: {str(e)}"}
