import asyncio
from playwright.async_api import async_playwright

url = 'https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page=1&aroundQuery=worldwide'
async def get_search_total_pages(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)

        # On attends que la page ait chargé le contenu avec le nombre total de pages
        await page.wait_for_selector('.sc-bhqpjJ.iCgvlm')

        # Récupération du nombre total de pages
        total_pages_text = await page.inner_text('.sc-bhqpjJ.iCgvlm')

        await browser.close()

        return total_pages_text.split("\n")[-1]

# Exécutez la fonction asynchrone
total_pages = asyncio.run(get_search_total_pages(url))