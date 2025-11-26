from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import relationship
from .db import Base


class League(Base):
    __tablename__ = "leagues"
    id = Column(Integer, primary_key=True, index=True)
    tm_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    country = Column(String, index=True)
    url = Column(String, unique=True)

class Club(Base):
    __tablename__ = "clubs"
    id = Column(Integer, primary_key=True, index=True)
    tm_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    url = Column(String, unique=True)
    league_id = Column(Integer, ForeignKey("leagues.id"))
    league = relationship("League")

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)

    tm_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)

    birth_date = Column(Date, nullable=True)
    nationality = Column(String, index=True)
    position = Column(String, index=True)
    height_cm = Column(Integer, nullable=True)
    foot = Column(String, nullable=True)

    current_club = Column(String, index=True)
    market_value_eur = Column(Float, nullable=True)
    contract_until = Column(Date, nullable=True)
    agent = Column(String, nullable=True)

    scraped = Column(Boolean, default=False, index=True)
    description_raw = Column(Text, nullable=True)

Index("ix_players_name_tm_id", Player.name, Player.tm_id)
