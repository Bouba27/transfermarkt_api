# Transfermarkt-like API (FastAPI)

This project scrapes Transfermarkt to build a local database of leagues, clubs, and players, then exposes a REST API.

## Quick start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
python scripts/run_crawler.py    # fills player IDs
python scripts/run_scraper.py    # scrapes player profiles
uvicorn app.main:app --reload
```

API docs available at:
http://127.0.0.1:8000/docs

## Notes
- Transfermarkt has no public official API; this is scraping-based and may be against their ToS.
- Scraping the whole world will take a long time; scripts are resumable.
