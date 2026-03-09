from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import attendance, auth, employees

app = FastAPI(
    title="HRMS Lite API",
    version="1.0.0",
    description="Human Resource Management System Lite backend service.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["System"])
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(employees.router)
app.include_router(attendance.router)
app.include_router(auth.router)
