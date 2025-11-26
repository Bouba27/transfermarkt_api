from playwright.async_api import async_playwright
import random

USER_AGENTS = [
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"),
    ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
     "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"),
    ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
     "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"),
]

async def get_page():
    p = await async_playwright().start()
    browser = await p.firefox.launch(headless=True)
    ctx = await browser.new_context(user_agent=random.choice(USER_AGENTS))
    page = await ctx.new_page()
    return p, browser, ctx, page
