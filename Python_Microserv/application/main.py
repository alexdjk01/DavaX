from fastapi import FastAPI
from application.db.session import init_db
from application.api import pow_api, factorial_api, fibonacci_api

app = FastAPI(title="Python Microservice", version="1.0")
init_db()
app.include_router(pow_api.router)
app.include_router(factorial_api.router)
app.include_router(fibonacci_api.router)



@app.get("/")
def read_root():
    return {"message": "Python Course Homework Microservice started successfully"}

# DEBUG TEMPORAR
import sys
if "uvicorn" in sys.argv[0]:
    print("✔ Rute înregistrate:")
    for route in app.routes:
        print(f"{route.path} -> {route.name}")