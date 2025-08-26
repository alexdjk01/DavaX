from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from application.services.factorial_service import calculate_factorial
from application.db.session import SessionLocal
from application.models.db_model import MathOperation
import json
from application.utils.stream_writer import publish_to_stream


router = APIRouter()


class FactorialRequest(BaseModel):
    number: int


class FactorialResponse(BaseModel):
    result: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/factorial", response_model=FactorialResponse)
def compute_factorial(request: FactorialRequest, db: Session = Depends(get_db)):
    publish_to_stream({
        "operation": "factorial",
        "input": request.dict()
    })
    try:
        result = calculate_factorial(request.number)
        operation = MathOperation(
            operation="factorial",
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
            operation="factorial",
            input_data=json.dumps({"number": request.number}),
            result=str(e),
            status="error",
        )
        db.add(operation)
        db.commit()
        return {"result": f"Error: {str(e)}"}
