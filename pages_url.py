import asyncio
from playwright.async_api import async_playwright



async def get_search_total_pages(baseurl: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(baseurl)

        # On attends que la page ait chargé le contenu avec le nombre total de pages
        await page.wait_for_selector('.sc-bhqpjJ.iCgvlm')

        # Récupération du nombre total de pages
        total_pages_text = await page.inner_text('.sc-bhqpjJ.iCgvlm')

        await browser.close()

        # Ne retourne que le dernier élément du selecteur qui correspond à la dernière page
        return total_pages_text.split("\n")[-1]

# Exécutez la fonction asynchrone
#total_pages = asyncio.run(get_search_total_pages(url))



async def extract_links(url: str, selector: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)

        # Wait for the page to load the content
        await page.wait_for_selector(selector)

        # Select all elements matching the selector
        elements = await page.query_selector_all(selector)

        # Extract the links using get_attribute
        links = [await element.get_attribute("href") for element in elements]

        await browser.close()

        return links

baseurl = 'https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page=1&aroundQuery=worldwide'
#url = 'https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page=1&aroundQuery=worldwide'
selector = '.sc-6i2fyx-0.gIvJqh'

page_number = asyncio.run(get_search_total_pages(baseurl))

for i in range(1, 3):
    url = f'https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page={i}&aroundQuery=worldwide'
    links = asyncio.run(extract_links(url, selector))
    print("\n".join(links))

