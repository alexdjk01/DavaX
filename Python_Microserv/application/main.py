from fastapi import FastAPI
from application.db.session import init_db

init_db()

app = FastAPI(title="Python Microservice", version="1.0")


@app.get("/")
def read_root():
    return {"message": "Python Course Homework Microservice started successfully"}
