from fastapi import FastAPI
from .db import Base, engine
from .routes.players import router as players_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Transfermarkt-like API")

app.include_router(players_router, prefix="/players", tags=["players"])

