"""
This module contains all the functions needed to manage pagination and retrieve pages from html code.
"""

import logging

import httpx
import validators
from fake_useragent import UserAgent
from playwright.async_api import TimeoutError, async_playwright
from selectolax.parser import HTMLParser

logger = logging.getLogger("scrap_wttj.pagination_functions")


async def get_html(url: str):
    """
    Function for parsing the required html page.
    A different UserAgent is used for each function call to avoid being blocked by the scraped site.
    :param url: url of the page we want to scrape (job details pages)
    """
    user_agent = UserAgent().random  # Generate a random User-Agent for each call
    headers = {"User-Agent": user_agent}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = HTMLParser(resp.text)
        except httpx.HTTPError as e:
            logging.error(f"HTTP error while fetching {url}: {e}")
            return None
        except Exception as e:
            logging.error(f"An error occurred while fetching {url}: {e}")
            return None
    return html


import logging

import validators
from playwright.async_api import TimeoutError, async_playwright


async def get_total_pages(baseurl: str, total_page_selector: str):
    """
    Function to return the total number of pages in our search.
    Use of playwright because the page is coded in JavaScript.

    :param baseurl: URL of the first page returned after entering the desired job in the search bar.
    :param total_page_selector: JavaScript selector containing the number of pages.
    :return int: The number corresponding to the last page of our search.
    """
    max_attempts = 2
    attempt = 0

    while attempt < max_attempts:
        try:
            if not validators.url(baseurl):
                raise ValueError("Invalid URL")

            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                try:
                    await page.goto(baseurl, timeout=5000)

                    # Wait until the page has loaded the content with the total number of pages
                    await page.wait_for_selector(total_page_selector, timeout=5000)

                    # Retrieve total number of pages
                    total_pages_text = await page.inner_text(total_page_selector)

                    # Check that the operation was successful and that the resulting list is not empty
                    total_pages = int((total_pages_text.split("\n"))[-1])
                    return total_pages if total_pages else None

                except TimeoutError as e:
                    logging.error(
                        f"Timeout error while extracting total number of pages: {str(e)}"
                    )
                except Exception as e:
                    logging.error(
                        f"Error while extracting total number of pages: {str(e)}"
                    )
                finally:
                    await browser.close()

        except ValueError as ve:
            logging.error(f"Invalid URL: {str(ve)}")
            break
        except Exception as e:
            logging.error(f"Error while processing the base URL: {str(e)}")

        logging.info(f"Retrying... Attempt {attempt + 1} of {max_attempts}")
        attempt += 1

    logging.error("Failed to retrieve total number of pages after multiple attempts")
    return None
