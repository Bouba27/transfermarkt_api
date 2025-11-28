from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Player, Club, League, Transfer
from app.routes.players import router as players_router

app = FastAPI(title="Transfermarkt API")

@app.get("/")
def root():
    return {"status": "ok"}

# Routes joueurs (search)
app.include_router(players_router, prefix="/players", tags=["players"])

@app.get("/debug/counts")
def debug_counts(db: Session = Depends(get_db)):
    return {
        "players": db.query(Player).count(),
        "clubs": db.query(Club).count(),
        "leagues": db.query(League).count(),
        "transfers": db.query(Transfer).count(),
    }
