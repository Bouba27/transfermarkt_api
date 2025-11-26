from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def search_players(
    q: str | None = Query(None, description="Search by name"),
    club: str | None = None,
    nationality: str | None = None,
    position: str | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    scraped_only: bool = True,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(models.Player)

    if scraped_only:
        query = query.filter(models.Player.scraped == True)

    if q:
        query = query.filter(models.Player.name.ilike(f"%{q}%"))
    if club:
        query = query.filter(models.Player.current_club.ilike(f"%{club}%"))
    if nationality:
        query = query.filter(models.Player.nationality.ilike(f"%{nationality}%"))
    if position:
        query = query.filter(models.Player.position.ilike(f"%{position}%"))
    if min_value is not None:
        query = query.filter(models.Player.market_value_eur >= min_value)
    if max_value is not None:
        query = query.filter(models.Player.market_value_eur <= max_value)

    return query.offset(offset).limit(limit).all()

@router.get("/{tm_id}")
def get_player(tm_id: str, db: Session = Depends(get_db)):
    pl = db.query(models.Player).filter(models.Player.tm_id == tm_id).first()
    if not pl:
        raise HTTPException(404, "Player not found")
    return pl
