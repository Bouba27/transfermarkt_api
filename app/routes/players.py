from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Player

router = APIRouter()

@router.get("/")
def search_players(
    q: str = "",
    scraped_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Player)

    if q:
        query = query.filter(Player.name.ilike(f"%{q}%"))

    if scraped_only:
        query = query.filter(Player.scraped == True)

    results = query.offset(offset).limit(limit).all()
    return results
