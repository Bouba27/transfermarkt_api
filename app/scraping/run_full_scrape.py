# app/scraping/run_full_scrape.py

import asyncio
from scraper_leagues import scrape_leagues
from scraper_clubs import scrape_clubs
from scraper_players import scrape_players
from scrape_player_details import main as scrape_details


async def run_all():
    print("=== Scraping ligues ===")
    await scrape_leagues()

    print("=== Scraping clubs ===")
    await scrape_clubs()

    print("=== Scraping joueurs ===")
    await scrape_players()

    print("=== Scraping détails joueurs ===")
    await scrape_details()

    print("=== SCRAPING GLOBAL TERMINÉ ===")


if __name__ == "__main__":
    asyncio.run(run_all())
