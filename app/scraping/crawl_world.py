import re
from bs4 import BeautifulSoup
from tenacity import retry, wait_fixed, stop_after_attempt
from tqdm import tqdm
from .browser import get_page

BASE = "https://www.transfermarkt.com"

@retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
async def fetch_html(page, url):
    await page.goto(url, timeout=60000)
    await page.wait_for_timeout(1000)
    return await page.content()

def extract_league_links(html):
    soup = BeautifulSoup(html, "lxml")
    leagues = []

    for a in soup.select("a[href*='/startseite/wettbewerb/']"):
        href = a.get("href", "")
        m = re.search(r"/startseite/wettbewerb/([A-Z0-9]+)", href)
        if not m:
            continue
        tm_id = m.group(1)
        name = a.get_text(strip=True)

        country = ""
        parent = a.find_parent("table")
        if parent:
            cap = parent.select_one("caption")
            if cap:
                country = cap.get_text(strip=True)

        url = BASE + href.split("?")[0]
        leagues.append((tm_id, name, country, url))

    uniq = {}
    for tm_id, name, country, url in leagues:
        uniq[tm_id] = (tm_id, name, country, url)
    return list(uniq.values())

def extract_club_links_from_league(html):
    soup = BeautifulSoup(html, "lxml")
    clubs = []

    for a in soup.select("a[href*='/startseite/verein/']"):
        href = a.get("href", "")
        m = re.search(r"/startseite/verein/(\d+)", href)
        if not m:
            continue
        tm_id = m.group(1)
        name = a.get_text(strip=True)
        url = BASE + href.split("?")[0]
        clubs.append((tm_id, name, url))

    uniq = {}
    for tm_id, name, url in clubs:
        uniq[tm_id] = (tm_id, name, url)
    return list(uniq.values())

def build_roster_url(club_url):
    return club_url.replace("/startseite/verein/", "/kader/verein/") + "/saison_id/2025"

def extract_player_ids_from_roster(html):
    soup = BeautifulSoup(html, "lxml")
    players = []

    for a in soup.select("a[href*='/profil/spieler/']"):
        href = a.get("href", "")
        m = re.search(r"/profil/spieler/(\d+)", href)
        if not m:
            continue
        tm_id = m.group(1)
        name = a.get_text(strip=True)
        players.append((tm_id, name))

    uniq = {}
    for tm_id, name in players:
        if tm_id not in uniq:
            uniq[tm_id] = (tm_id, name)
    return list(uniq.values())

WORLD_PAGES = [
    f"{BASE}/wettbewerbe/europa",
    f"{BASE}/wettbewerbe/amerika",
    f"{BASE}/wettbewerbe/asien",
    f"{BASE}/wettbewerbe/afrika",
    f"{BASE}/wettbewerbe/australien",
]

async def crawl_world():
    p, browser, ctx, page = await get_page()
    leagues_all = []
    clubs_by_league = {}
    players_by_club = {}

    try:
        for world_url in WORLD_PAGES:
            html = await fetch_html(page, world_url)
            leagues = extract_league_links(html)
            leagues_all.extend(leagues)

        uniq_leagues = {}
        for lg in leagues_all:
            uniq_leagues[lg[0]] = lg
        leagues_all = list(uniq_leagues.values())

        for tm_id, name, country, lg_url in tqdm(leagues_all, desc="Leagues -> Clubs"):
            html = await fetch_html(page, lg_url)
            clubs = extract_club_links_from_league(html)
            clubs_by_league[tm_id] = clubs

        for lg_id, clubs in tqdm(clubs_by_league.items(), desc="Clubs -> Rosters"):
            for club_tm_id, club_name, club_url in clubs:
                roster_url = build_roster_url(club_url)
                html = await fetch_html(page, roster_url)
                players = extract_player_ids_from_roster(html)
                players_by_club[club_tm_id] = players
                await page.wait_for_timeout(800)

        return leagues_all, clubs_by_league, players_by_club

    finally:
        await ctx.close()
        await browser.close()
        await p.stop()
