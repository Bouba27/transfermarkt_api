# app/scraping/scraper_players_details.py

import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Player, Transfer

BASE_URL = "https://www.transfermarkt.fr"


def clean_int(text):
    if not text:
        return None
    digits = "".join(c for c in text if c.isdigit())
    return int(digits) if digits else None


def parse_market_value(text):
    if not text:
        return None
    txt = (
        text.lower()
        .replace("€", "")
        .replace("mio.", "")
        .replace("millions", "")
        .replace(",", ".")
        .strip()
    )
    try:
        return float(txt)
    except:
        return None


async def scrape_details_for_player(page, player: Player, db: Session):
    url = player.url or f"{BASE_URL}/profil/spieler/{player.tm_id}"
    await page.goto(url, timeout=60000)
    html = await page.content()
    soup = BeautifulSoup(html, "lxml")

    # --- Infos principales ---
    name_el = soup.select_one("h1.spielername")
    if name_el:
        player.name = name_el.text.strip()

    club_el = soup.select_one("div.dataValue a.vereinprofil_tooltip")
    if club_el:
        player.current_club = club_el.text.strip()

    nat_el = soup.select_one("span.flaggenrahmen + a")
    if nat_el:
        player.nationality = nat_el.text.strip()

    pos_el = soup.select_one("span.dataValue span:not(.flaggenrahmen)")
    if pos_el:
        player.position = pos_el.text.strip()

    value_el = soup.select_one("div.dataMarktwert span.mw")
    if value_el:
        mv_mio = parse_market_value(value_el.text)
        if mv_mio:
            player.market_value_eur = mv_mio * 1_000_000

    # --- Historique des transferts ---
    db.query(Transfer).filter_by(player_id=player.id).delete()
    db.commit()

    transfer_table = soup.select_one("table#transfers")
    if transfer_table:
        for row in transfer_table.select("tbody tr"):
            cols = row.select("td")
            if len(cols) < 5:
                continue
            db.add(
                Transfer(
                    player_id=player.id,
                    season=cols[0].text.strip(),
                    date=cols[1].text.strip(),  # texte brut
                    from_club=cols[2].text.strip(),
                    to_club=cols[3].text.strip(),
                    fee=cols[4].text.strip(),
                )
            )

    player.scraped = True
    db.commit()


async def main():
    db = SessionLocal()
    players = db.query(Player).filter(Player.scraped == False).all()

    print(f"{len(players)} joueurs à compléter.")

    async with async_playwright() as pw:
        browser = await pw.firefox.launch(headless=True)
        page = await browser.new_page()

        for idx, player in enumerate(players, 1):
            print(f"[{idx}/{len(players)}] Scraping détails : {player.name}")
            try:
                await scrape_details_for_player(page, player, db)
            except Exception as e:
                print("ERREUR:", e)

        await browser.close()

    db.close()
    print("=== Détails joueurs complétés ===")


if __name__ == "__main__":
    asyncio.run(main())
