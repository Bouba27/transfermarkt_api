# app/scraping/scraper_clubs.py

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from app.db import SessionLocal
from app.models import League, Club

BASE_URL = "https://www.transfermarkt.fr"


async def scrape_clubs():
    db = SessionLocal()
    leagues = db.query(League).all()

    async with async_playwright() as pw:
        browser = await pw.firefox.launch(headless=True)
        page = await browser.new_page()

        for lg in leagues:
            print(f"Scraping clubs de : {lg.name}")
            await page.goto(lg.url, timeout=60000)

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            club_links = soup.select("a.vereinprofil_tooltip")

            for c in club_links:
                name = c.text.strip()
                url = BASE_URL + c["href"]
                tm_id = c["href"].split("/")[-1]

                exists = db.query(Club).filter_by(tm_id=tm_id).first()
                if not exists:
                    db.add(
                        Club(
                            name=name,
                            tm_id=tm_id,
                            url=url,
                            league_id=lg.id
                        )
                    )
                    db.commit()
                    print(f"  → Club ajouté : {name}")

        await browser.close()
    db.close()
    print("=== Clubs enregistrés ===")
