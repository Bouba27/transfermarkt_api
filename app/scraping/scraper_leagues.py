# app/scraping/scraper_leagues.py

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from app.db import SessionLocal
from app.models import League

BASE_URL = "https://www.transfermarkt.fr"
LEAGUES_URL = BASE_URL + "/wettbewerbe/europa"


async def scrape_leagues():
    db = SessionLocal()

    async with async_playwright() as pw:
        browser = await pw.firefox.launch(headless=True)
        page = await browser.new_page()

        await page.goto(LEAGUES_URL, timeout=60000)
        html = await page.content()
        soup = BeautifulSoup(html, "lxml")

        league_links = soup.select("a.wettbewerbs-link")

        for lg in league_links:
            name = lg.text.strip()
            url = BASE_URL + lg["href"]
            tm_id = lg["href"].split("/")[-1]

            exists = db.query(League).filter_by(tm_id=tm_id).first()
            if not exists:
                db.add(League(name=name, tm_id=tm_id, url=url))
                db.commit()
                print(f"✓ Ligue ajoutée : {name}")

        await browser.close()
    db.close()
    print("=== Ligues enregistrées ===")

