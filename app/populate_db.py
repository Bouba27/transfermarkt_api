# populate_db.py
import asyncio
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Player
from bs4 import BeautifulSoup

BASE_URL = "https://www.transfermarkt.fr"

async def scrape_player(page, url):
    await page.goto(url, timeout=60000)
    html = await page.content()
    soup = BeautifulSoup(html, "lxml")

    name = soup.select_one("h1.spielername").text.strip()
    nationality = soup.select_one(".dataValue a.flaggenrahmen")["title"]
    position = soup.select_one(".detail-positionen a").text.strip()

    return {
        "tm_id": url.split("/")[-1],
        "name": name,
        "nationality": nationality,
        "position": position,
        "scraped": True,
    }

async def main():
    db: Session = SessionLocal()

    async with async_playwright() as pw:
        browser = await pw.firefox.launch()
        page = await browser.new_page()

        await page.goto(BASE_URL + "/ligue-1/startseite/wettbewerb/FR1", timeout=60000)
        html = await page.content()
        soup = BeautifulSoup(html, "lxml")

        player_links = [
            BASE_URL + a["href"]
            for a in soup.select("a.spielprofil_tooltip")[:10]
        ]

        for link in player_links:
            data = await scrape_player(page, link)

            existing = db.query(Player).filter(Player.tm_id == data["tm_id"]).first()
            if not existing:
                db.add(Player(**data))
                db.commit()

        await browser.close()
    print("Scraping terminé. Données insérées !")

if __name__ == "__main__":
    asyncio.run(main())
