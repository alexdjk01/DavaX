from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class MathOperation(Base):
    __tablename__ = "python_operations"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)
    input_data = Column(Text, nullable=False)  # Json Serializ
    result = Column(String, nullable=False)
    status = Column(String, default="success")  # success sau error
    created_at = Column(DateTime, default=datetime.utcnow())
