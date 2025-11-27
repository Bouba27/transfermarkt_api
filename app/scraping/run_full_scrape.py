# app/scraping/run_full_scrape.py
import asyncio
from app.scraping.scraper_leagues import scrape_leagues
from app.scraping.scraper_clubs import scrape_clubs
from app.scraping.scraper_players import scrape_players
from app.scraping.scraper_players_details import main as scrape_players_details_main

async def run_all():
    print("=== Scraping ligues ===")
    await scrape_leagues()

    print("=== Scraping clubs ===")
    await scrape_clubs()

    print("=== Scraping joueurs ===")
    await scrape_players()

    print("=== Scraping détails joueurs ===")
    await scrape_players_details_main()

    print("=== SCRAPING GLOBAL TERMINÉ ===")

if __name__ == "__main__":
    asyncio.run(run_all())

