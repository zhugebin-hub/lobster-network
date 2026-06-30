#!/usr/bin/env python3
"""Render HTML slides to PNG images using Playwright."""
import asyncio
import os
from playwright.async_api import async_playwright

SLIDE_DIR = "/home/admin/.openclaw/workspace/slide-deck/jingangjing-outline"
HTML_FILE = os.path.join(SLIDE_DIR, "slides.html")
OUTPUT_DIR = SLIDE_DIR

SLIDE_NAMES = [
    "01-slide-cover",
    "02-slide-yuanqi",
    "03-slide-fawen",
    "04-slide-zonggang",
    "05-slide-poxiang",
    "06-slide-wude",
    "07-slide-guowei",
    "08-slide-fude",
    "09-slide-lixing",
    "10-slide-wuwo",
    "11-slide-jieyu",
    "12-slide-back-cover",
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=2,  # 2x for sharper images
        )
        page = await context.new_page()

        file_url = f"file://{HTML_FILE}"
        await page.goto(file_url, wait_until="networkidle")

        # Wait for fonts to load
        await page.wait_for_timeout(2000)

        for i, slide_name in enumerate(SLIDE_NAMES, 1):
            slide_id = f"slide-{i}"
            element = page.locator(f"#{slide_id}")

            if await element.count() > 0:
                output_path = os.path.join(OUTPUT_DIR, f"{slide_name}.png")
                await element.screenshot(path=output_path, type="png")
                print(f"✓ Generated: {slide_name}.png")
            else:
                print(f"✗ Not found: {slide_id}")

        await browser.close()
        print("\nAll slides generated!")

if __name__ == "__main__":
    asyncio.run(main())
