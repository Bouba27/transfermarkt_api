# app/scraping/scraper_players.py

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from app.db import SessionLocal
from app.models import Club, Player

BASE_URL = "https://www.transfermarkt.fr"


async def scrape_players():
    db = SessionLocal()
    clubs = db.query(Club).all()

    async with async_playwright() as pw:
        browser = await pw.firefox.launch(headless=True)
        page = await browser.new_page()

        for club in clubs:
            print(f"Scraping joueurs du club : {club.name}")
            await page.goto(club.url, timeout=60000)

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            player_links = soup.select("a.spielprofil_tooltip")

            for p in player_links:
                name = p.text.strip()
                url = BASE_URL + p["href"]
                tm_id = p["href"].split("/")[-1]

                exists = db.query(Player).filter_by(tm_id=tm_id).first()
                if not exists:
                    db.add(
                        Player(
                            name=name,
                            tm_id=tm_id,
                            url=url,
                            scraped=False
                        )
                    )
                    db.commit()
                    print(f"  → Joueur ajouté : {name}")

        await browser.close()
    db.close()
    print("=== Joueurs enregistrés ===")
