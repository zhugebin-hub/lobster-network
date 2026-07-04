#!/usr/bin/env python3
"""Render each slide HTML to PNG using Playwright (system Chrome has CJK fonts)."""
import asyncio
import os
from playwright.async_api import async_playwright

SLIDE_DIR = "/home/admin/.openclaw/workspace/slide-deck/jingangjing-outline"
ALL_HTML = os.path.join(SLIDE_DIR, "all-slides.html")

SLIDE_IDS = [
    "slide-1", "slide-2", "slide-3", "slide-4", "slide-5", "slide-6",
    "slide-7", "slide-8", "slide-9", "slide-10", "slide-11", "slide-12"
]

SLIDE_NAMES = [
    "01-slide-cover", "02-slide-yuanqi", "03-slide-fawen", "04-slide-zonggang",
    "05-slide-poxiang", "06-slide-wude", "07-slide-guowei", "08-slide-fude",
    "09-slide-lixing", "10-slide-wuwo", "11-slide-jieyu", "12-slide-back-cover"
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
        page = await context.new_page()

        file_url = f"file://{ALL_HTML}"
        await page.goto(file_url, wait_until="load")
        await page.wait_for_timeout(2000)

        for slide_id, name in zip(SLIDE_IDS, SLIDE_NAMES):
            element = page.locator(f"#{slide_id}")
            count = await element.count()
            if count > 0:
                output = os.path.join(SLIDE_DIR, f"{name}.png")
                await element.screenshot(path=output, type="png")
                print(f"OK: {name}.png")
            else:
                print(f"MISSING: {slide_id}")

        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
