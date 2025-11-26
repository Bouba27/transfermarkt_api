import re, json
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from tenacity import retry, wait_fixed, stop_after_attempt
from .browser import get_page

BASE = "https://www.transfermarkt.com"

@retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
async def fetch_html(page, url):
    await page.goto(url, timeout=60000)
    await page.wait_for_timeout(1000)
    return await page.content()

def parse_market_value(text):
    if not text:
        return None
    t = text.replace("€", "").replace(",", ".").strip().lower()
    try:
        if "m" in t:
            return float(t.replace("m", "")) * 1_000_000
        if "k" in t:
            return float(t.replace("k", "")) * 1_000
        return float(t)
    except:
        return None

def parse_player(html):
    soup = BeautifulSoup(html, "lxml")

    name_el = soup.select_one("h1.data-header__headline-wrapper")
    name = name_el.get_text(strip=True) if name_el else None

    mv_el = soup.select_one(".tm-player-market-value-development__current-value")
    market_value_eur = parse_market_value(mv_el.get_text(strip=True)) if mv_el else None

    nationality, position, height_cm, foot, birth_date = None, None, None, None, None
    items = soup.select(".data-header__details ul li")

    for li in items:
        t = li.get_text(" ", strip=True)

        if "Citizenship" in t or "Nationalität" in t:
            img = li.select_one("img")
            nationality = img["title"] if img and img.has_attr("title") else t.split(":")[-1].strip()

        if "Position" in t:
            position = t.split(":")[-1].strip()

        if "Height" in t or "Größe" in t:
            m = re.search(r"(\d{2,3})\s?cm", t)
            height_cm = int(m.group(1)) if m else None

        if "Foot" in t or "Fuß" in t:
            foot = t.split(":")[-1].strip()

        if "Date of birth" in t or "Geburtsdatum" in t:
            m = re.search(r"(\w+\s\d{1,2},\s\d{4}|\d{1,2}\.\d{1,2}\.\d{4})", t)
            if m:
                try:
                    birth_date = dateparser.parse(m.group(1), dayfirst=True).date()
                except:
                    birth_date = None

    club_el = soup.select_one(".data-header__club a")
    current_club = club_el.get_text(strip=True) if club_el else None

    contract_until = None
    contract_label = soup.find(string=re.compile("Contract expires|Vertrag bis"))
    if contract_label:
        try:
            date_txt = contract_label.find_parent("li").get_text(" ", strip=True).split(":")[-1].strip()
            contract_until = dateparser.parse(date_txt, dayfirst=True).date()
        except:
            contract_until = None

    agent = None
    agent_label = soup.find(string=re.compile("Player agent|Berater"))
    if agent_label:
        try:
            agent = agent_label.find_parent("li").get_text(" ", strip=True).split(":")[-1].strip()
        except:
            agent = None

    raw_json = {
        "html_snapshot": html[:250000]
    }

    return {
        "name": name,
        "nationality": nationality,
        "position": position,
        "height_cm": height_cm,
        "foot": foot,
        "birth_date": birth_date,
        "current_club": current_club,
        "market_value_eur": market_value_eur,
        "contract_until": contract_until,
        "agent": agent,
        "description_raw": json.dumps(raw_json)
    }

async def scrape_player(tm_id: str):
    url = f"{BASE}/player/profil/spieler/{tm_id}"
    p, browser, ctx, page = await get_page()
    try:
        html = await fetch_html(page, url)
        return parse_player(html)
    finally:
        await ctx.close()
        await browser.close()
        await p.stop()
