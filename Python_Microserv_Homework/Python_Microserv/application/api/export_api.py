from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from application.db.session import SessionLocal
from application.services.export_service import export_operations_to_csv


router = APIRouter(
    prefix="",
    tags=["Export"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/export")
def export_csv(
    operation: str = Query(None, description="Filter by operation"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
    ):
    csv_data = export_operations_to_csv(db, operation, status)
    response = StreamingResponse(
        iter([csv_data]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=operations_export.csv"
    return response
