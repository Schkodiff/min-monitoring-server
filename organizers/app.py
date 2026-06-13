import os

from sqlmodel import SQLModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import *
from config.database import engine, seed_api_key
from routers import organizer
from routers import request


app = FastAPI(title="Organizers Project")

# Список разрешенных источников (доменов)
def get_cors_origins() -> list[str]:
    origins = os.getenv("CORS_ORIGINS")
    if origins:
        return [origin.strip() for origin in origins.split(",") if origin.strip()]
    return ["http://localhost:5173"]


origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # разрешить все: ["*"]
    allow_credentials=True, # не знаю для чего
    allow_methods=["*"],    # разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],    # разрешить все заголовки 
)


def create_db():
    SQLModel.metadata.create_all(engine)
    
app.include_router(organizer.router, prefix="/organizers", tags=["organizers"])
app.include_router(request.router, prefix="/requests", tags=["requests"])

@app.on_event("startup")
def on_startup():
    create_db()
    seed_api_key()

@app.get("/")
async def root():
    return {"message": "Organizers Project"}
