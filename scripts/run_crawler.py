import asyncio
from app.db import SessionLocal, Base, engine
from app.scraping.crawl_world import crawl_world
from app import crud

Base.metadata.create_all(bind=engine)

async def main():
    leagues, clubs_by_league, players_by_club = await crawl_world()

    db = SessionLocal()
    try:
        for lg_tm_id, lg_name, lg_country, lg_url in leagues:
            lg = crud.upsert_league(db, lg_tm_id, lg_name, lg_country, lg_url)

            clubs = clubs_by_league.get(lg_tm_id, [])
            for club_tm_id, club_name, club_url in clubs:
                cl = crud.upsert_club(db, club_tm_id, club_name, club_url, lg.id)

                players = players_by_club.get(club_tm_id, [])
                for pl_tm_id, pl_name in players:
                    crud.add_player_stub(db, pl_tm_id, pl_name)

        print("Crawler terminé.")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
