from fastapi import FastAPI
from application.db.session import init_db
from application.api import pow_api, factorial_api, fibonacci_api, gcd_api, lcm_api, sqrt_api, log_api, export_api
from fastapi.middleware.cors import CORSMiddleware
from application.middlewares.logging_middleware import LoggingMiddleware

# Using FastAPI for convenience
app = FastAPI(title="Python Microservice", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sau specific: ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Middleware pentru logging de mesaje in consola
app.add_middleware(LoggingMiddleware)
# Instanta de SQL database local
init_db()
# Routere pentru actiuni specifice
app.include_router(pow_api.router)
app.include_router(factorial_api.router)
app.include_router(fibonacci_api.router)
app.include_router(gcd_api.router)
app.include_router(lcm_api.router)
app.include_router(sqrt_api.router)
app.include_router(log_api.router)
app.include_router(export_api.router)


# Home path care se deschide cand pornim serverul
@app.get("/")
def read_root():
    return {"message": "Python Course Homework Microservice started successfully"}


# DEBUG TEMPORAR
import sys

if "uvicorn" in sys.argv[0]:
    print("Test registered routes for DEBUG:")
    for route in app.routes:
        print(f"{route.path} -> {route.name}")
