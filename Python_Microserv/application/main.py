from fastapi import FastAPI
from application.db.session import init_db
from application.api import pow_api, factorial_api, fibonacci_api
from fastapi.middleware.cors import CORSMiddleware

# Using FastAPI for convenience
app = FastAPI(title="Python Microservice", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sau specific: ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialization of the SQLite local database
init_db()
# Routers linkers to logic
app.include_router(pow_api.router)
app.include_router(factorial_api.router)
app.include_router(fibonacci_api.router)


# Root path when server start
@app.get("/")
def read_root():
    return {"message": "Python Course Homework Microservice started successfully"}


# DEBUG TEMPORAR
import sys

if "uvicorn" in sys.argv[0]:
    print("Test registered routes for DEBUG:")
    for route in app.routes:
        print(f"{route.path} -> {route.name}")
