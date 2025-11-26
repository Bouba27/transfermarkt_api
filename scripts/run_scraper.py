import asyncio
from tqdm import tqdm
from app.db import SessionLocal, Base, engine
from app.scraping.scrape_player import scrape_player
from app import models, crud

Base.metadata.create_all(bind=engine)

CONCURRENCY = 2
SLEEP_MS = 1200

async def worker(queue):
    db = SessionLocal()
    try:
        while True:
            tm_id = await queue.get()
            if tm_id is None:
                queue.task_done()
                break

            try:
                data = await scrape_player(tm_id)
                crud.upsert_player_full(db, tm_id, data)
            except Exception as e:
                print("Scrape error", tm_id, e)

            await asyncio.sleep(SLEEP_MS / 1000)
            queue.task_done()
    finally:
        db.close()

async def main():
    db = SessionLocal()
    try:
        ids = [p.tm_id for p in db.query(models.Player).filter(models.Player.scraped == False).all()]
    finally:
        db.close()

    queue = asyncio.Queue()
    for tm_id in ids:
        queue.put_nowait(tm_id)

    workers = [asyncio.create_task(worker(queue)) for _ in range(CONCURRENCY)]

    for _ in workers:
        queue.put_nowait(None)

    for _ in tqdm(range(len(ids)), desc="Scraping players"):
        await queue.get()
        queue.task_done()

    await queue.join()
    for w in workers:
        await w

    print("Scraper terminé.")

if __name__ == "__main__":
    asyncio.run(main())
