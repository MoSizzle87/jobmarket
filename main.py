import validators
from random import uniform
import logging
import sys
import asyncio
from scrap_wttj.constants import (BASEURL, RACINE_URL, TOTAL_PAGE_SELECTOR, JOB_LINK_SELECTOR, CONTRACT_INFO_SELECTOR,
                                  COMPANY_INFO_SELECTOR, CONTRACT_SELECTORS, COMPANY_SELECTORS)
from playwright.async_api import async_playwright
from scrap_wttj.data_extraction import extract_links, get_contract_elements, get_company_elements
from scrap_wttj.extraction_functions import get_total_pages, get_html
from scrap_wttj.file_operations import save_file


async def generate_job_search_url(page_number):
    return f"https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page={page_number}&aroundQuery=worldwide"


async def main():
    try:
        total_pages = await get_total_pages(BASEURL, TOTAL_PAGE_SELECTOR)
        wttj_database = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()

            for page_number in range(1, 2):
                job_search_url = await generate_job_search_url(page_number)
                page = await browser.new_page()
                job_links = await extract_links(page, job_search_url, JOB_LINK_SELECTOR)

                for i, link in enumerate(job_links, start=1):
                    print(f'Scraping page {page_number} offer {i}')
                    complete_url = f'{RACINE_URL}{link}'
                    html = get_html(complete_url)
                    if html:
                        # Use a dictionary for each job offer
                        contract_data = await get_contract_elements(html, CONTRACT_INFO_SELECTOR, CONTRACT_SELECTORS)
                        company_data = await get_company_elements(html, COMPANY_INFO_SELECTOR, COMPANY_SELECTORS)

                        # Individual items are added to the offer list
                        wttj_database.extend([contract_data, company_data])

                        # await asyncio.sleep(uniform(1, 3))
    except Exception as e:
        logging.error(f'Erreur inattendue : {e}')

    # Save the output in a json file
    save_file(wttj_database, 'wttj_database')


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit()
