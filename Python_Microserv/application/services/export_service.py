import csv
from io import StringIO
from sqlalchemy.orm import Session
from application.models.db_model import MathOperation


def export_operations_to_csv(db: Session, operation=None, status=None) -> str:
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["id", "operation", "input_data", "result", "status", "created_at"])

    query = db.query(MathOperation)
    if operation:
        query = query.filter(MathOperation.operation == operation)
    if status:
        query = query.filter(MathOperation.status == status)

    for row in query.order_by(MathOperation.created_at.desc()).all():
        writer.writerow([
            row.id, row.operation, row.input_data,
            row.result, row.status, row.created_at
        ])

    return output.getvalue()
