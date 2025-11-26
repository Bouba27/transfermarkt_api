from sqlalchemy.orm import Session
from . import models


def upsert_league(db: Session, tm_id: str, name: str, country: str, url: str):
    lg = db.query(models.League).filter(models.League.tm_id == tm_id).first()
    if not lg:
        lg = models.League(tm_id=tm_id, name=name, country=country, url=url)
        db.add(lg)
    else:
        lg.name = name
        lg.country = country
        lg.url = url
    db.commit()
    db.refresh(lg)
    return lg


def upsert_club(db: Session, tm_id: str, name: str, url: str, league_id: int):
    cl = db.query(models.Club).filter(models.Club.tm_id == tm_id).first()
    if not cl:
        cl = models.Club(tm_id=tm_id, name=name, url=url, league_id=league_id)
        db.add(cl)
    else:
        cl.name = name
        cl.url = url
        cl.league_id = league_id
    db.commit()
    db.refresh(cl)
    return cl


def add_player_stub(db: Session, tm_id: str, name: str | None = None):
    pl = db.query(models.Player).filter(models.Player.tm_id == tm_id).first()
    if not pl:
        pl = models.Player(tm_id=tm_id, name=name or "")
        db.add(pl)
        db.commit()
        db.refresh(pl)
    return pl


def upsert_player_full(db: Session, tm_id: str, data: dict):
    pl = db.query(models.Player).filter(models.Player.tm_id == tm_id).first()
    if not pl:
        pl = models.Player(tm_id=tm_id)
        db.add(pl)

    for k, v in data.items():
        setattr(pl, k, v)

    pl.scraped = True
    db.commit()
    db.refresh(pl)
    return pl
