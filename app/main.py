from fastapi import Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Player, Club, League, Transfer

@app.get("/debug/counts")
def debug_counts(db: Session = Depends(get_db)):
    return {
        "players": db.query(Player).count(),
        "clubs": db.query(Club).count(),
        "leagues": db.query(League).count(),
        "transfers": db.query(Transfer).count(),
    }



