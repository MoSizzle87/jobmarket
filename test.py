import validators
from random import uniform
from fake_useragent import UserAgent
import httpx
from selectolax.parser import HTMLParser
import asyncio
from playwright.async_api import async_playwright
import logging
import sys
import os
import json

# Liste des constantes
BASEURL = 'https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page=1&aroundQuery=worldwide'
RACINE_URL = 'https://www.welcometothejungle.com'
JOB_LINK_SELECTOR = '.sc-6i2fyx-0.gIvJqh'
TOTAL_PAGE_SELECTOR = '.sc-bhqpjJ.iCgvlm'
CONTRACT_INFO_SELECTOR = '.sc-bXCLTC.jlqIpd.sc-fbKhjd.kfysmu.sc-1wwpb2t-5.hexbEF'
COMPANY_INFO_SELECTOR = '.sc-bXCLTC.dBpdut'
CONTRACT_SELECTORS = {
    'job_title': '.sc-empnci.cYPTxs.wui-text',
    'contract_type': '[name="contract"]',
    'salary': '[name="salary"]',
    'company': '.sc-empnci.hmOCpj.wui-text',
    'location': '[name="location"]',
    'remote': '[name="remote"]',
    'experience': '[name="suitcase"]',
    'education_level': '[name="education_level"]'
    }
COMPANY_SELECTORS = {
    'sector': '[alt="Tag"]',
    'company_size': '[alt="Department"]',
    'creation_date': '[alt="Date"]',
    'address': '.sc-ezreuY.iObOsq.sc-boZgaH.fVBQVn.sc-4e9f7k-2.kAeJOl',
    'average_age_of_employees': '[alt="Birthday"]',
    'turnover_in_millions': '[alt="EuroCurrency"]',
    'proportion_female': '[alt="Female"]',
    'proportion_male': '[alt="Male"]'
}


async def get_total_pages(baseurl: str, total_page_selector: str):
    '''
    Fonction pour retourner le nombre de page totales de notre recherche.
    Utilisation de playwright xar il s'agit de code JavaScript
    :param baseurl: url de la première page de recherche
    :param selector: selecteur JavaScript contenant le nombre de pages
    :return: un nombre au format str correspondant à la dernière page de notre recherche
    '''
    try:
        if not validators.url(baseurl):
            raise ValueError("Invalid URL")

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            try:
                await page.goto(baseurl, timeout=5000)

                # On attends que la page ait chargé le contenu avec le nombre total de pages
                await page.wait_for_selector(total_page_selector, timeout=5000)

                # Récupération du nombre total de pages
                total_pages_text = await page.inner_text(total_page_selector)

                # Vérifier si l'opération a réussi et si la liste obtenue n'est pas vide
                pages = total_pages_text.split("\n")
                return int(pages[-1]) if pages else None
            except Exception as e:
                logging.error(f"Erreur pendant l'extraction du nombre total de pages: {str(e)}")
                raise
            finally:
                await browser.close()
    except ValueError as ve:
        logging.error(f"URL invalide: {str(ve)}")

async def extract_links(page, job_search_url: str, job_links_selector: str):
    '''
    Fonction pour extraire les liens vers les offres pour chaque page de recherche
    :param page: instance de la page Playwright
    :param url: url des pages de recherche
    :param selector: selecteur ou se trouve l'information
    :return: liste de liens
    '''
    try:
        await page.goto(job_search_url, timeout=5000)

        # On attends que la page ait chargé le contenu avec le nombre total de pages
        await page.wait_for_selector(job_links_selector, timeout=5000)

        # Selection de tous les éléments qui correspondent au selecteur
        elements = await page.query_selector_all(job_links_selector)

        # Extraction des liens en utilisant la commande get_attribute
        links = [await element.get_attribute("href") for element in elements]

        return links
    except Exception as e:
        print(f'Error extracting links: {str(e)}')
        return []


def get_html(url: str):
    """
    Parser la page html voulue
    On utilise un UserAgent différent à chaque appel de la fonction pour ne pas être bloqué par le site
    """
    user_agent = UserAgent().random  # Générer un User-Agent aléatoire à chaque appel
    headers = {'User-Agent': user_agent }

    with httpx.Client() as client:
        try:
            resp = client.get(url, headers=headers)
            html = HTMLParser(resp.text)
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            html = None
    return html


def get_info(html, selector, parent=True):
    replacements = {
        "Salaire : ": "", "Expérience : ": "", "Éducation : ": "", " collaborateurs": "", "Créée en ": "",
        "Âge moyen : ": "", " ans": "", "Chiffre d'affaires : ": "", "M€": "", "%": "", "&nbsp;": " ", "&NBSP;": " "
    }
    """
    Fonction pour extraire les informations voulues et revoyer None si l'information n'est pas présente dans la page
    :param html: HTML contenant les informations
    :param selector: HTML contenant les informations de variables
    :param replacements: Dictionnaire contenant les valeurs à supprimer et leurs remplacements
    :param parent: Indicateur si le selecteur doit aller chercher la balise parent
    :return: Texte contenant les informations
    """
    try:
        text = html.css_first(selector).parent.text() if parent else html.css_first(selector).text()
        for key, value in replacements.items():
            text = text.replace(key, value)
        return text
    except AttributeError:
        return None


async def get_contract_elements(html, contract_info_selector, database):
    """
    Extracts contract elements from HTML and updates the wttj_db with the extracted data.

    Args:
        html (HTML): The HTML containing the contract elements.
        database (dict): The database to update with the extracted data.

    Returns:
        dict: The extracted contract data.
    """
    # Ciblage de ma balise contenant toutes les données de base de l'offre
    contract_elements = html.css_first(contract_info_selector)

    try:
        job_title = get_info(contract_elements, CONTRACT_SELECTORS['job_title'], parent=False)
        contract_type = get_info(contract_elements, CONTRACT_SELECTORS['contract_type'])
        salary = get_info(contract_elements, CONTRACT_SELECTORS['salary'])
        company = get_info(contract_elements, CONTRACT_SELECTORS['company'], parent=False)
        location = get_info(contract_elements, CONTRACT_SELECTORS['location'])
        remote = get_info(contract_elements, CONTRACT_SELECTORS['remote'])
        experience = get_info(contract_elements, CONTRACT_SELECTORS['experience'])
        education_level = get_info(contract_elements, CONTRACT_SELECTORS['education_level'])
        # pour publication_date l'information figure directement dans la balise j'utilise .attributes
        publication_date = contract_elements.css_first('time').attributes['datetime'][0:10]

        contract_data = {
            'job_title': job_title, 'contract_type': contract_type, 'salary': salary, 'company': company,
            'location': location,
            'remote': remote, 'experience': experience, 'education_level': education_level,
            'publication_date': publication_date
        }
        await asyncio.sleep(uniform(1, 3))

        return contract_data
    except Exception as e:
        logging.error(f"Erreur pendant l'extraction des éléments du contrat: {e}")
        raise


async def get_company_elements(html, company_info_selector, database):
    try:
        company_elements = html.css_first(company_info_selector)

        sector = get_info(company_elements, COMPANY_SELECTORS['sector'])
        company_size = get_info(company_elements, COMPANY_SELECTORS['company_size'])
        creation_date = get_info(company_elements, COMPANY_SELECTORS['creation_date'])
        # Vérifiez si address est None avant d'appliquer split()
        address_info = get_info(company_elements, COMPANY_SELECTORS['address'], parent=False)
        address = ", ".join(address_info.split(", ")[:2]) if address_info else None
        average_age_of_employees = get_info(company_elements, COMPANY_SELECTORS['average_age_of_employees'])
        turnover_in_millions = get_info(company_elements, COMPANY_SELECTORS['turnover_in_millions'])
        proportion_female = get_info(company_elements, COMPANY_SELECTORS['proportion_female'])
        proportion_male = get_info(company_elements, COMPANY_SELECTORS['proportion_male'])

        company_data = {
            'sector': sector, 'company_size': company_size,
            'creation_date': creation_date, 'address': address, 'average_age_of_employees': average_age_of_employees,
            'turnover_in_millions': turnover_in_millions, 'proportion_female': proportion_female,
            'proportion_male': proportion_male
        }
        await asyncio.sleep(uniform(1, 3))

        return company_data

    except Exception as e:
        logging.error(f"Erreur pendant l'extraction des éléments de l'entreprise: {e}")
        raise

OUTPUT_DIR = '/Users/MoG/PycharmProjects/jobmarket/jobmarket'
def save_file(file_to_save, output_dir, output_name: str):
    output_name = f"{output_name}.json"
    output_path = os.path.join(output_dir, output_name)

    try:
        # Ouvre le fichier en mode écriture
        with open(output_path, 'w', encoding='utf-8') as fichier:
            # On utilise json.dump pour écrire les données dans le fichier JSON
            json.dump(file_to_save, fichier, ensure_ascii=False)

        print(f"Le document a été enregistré avec succès dans {output_path}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du document : {e}")


async def generate_job_search_url(page_number):
    return f"https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page={page_number}&aroundQuery=worldwide"


async def main():
    try:
        Total_pages = await get_total_pages(BASEURL, TOTAL_PAGE_SELECTOR)
        job_links = []
        wttj_database = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()

            for page_number in range(1, 2):
                job_search_url = await generate_job_search_url(page_number)
                page = await browser.new_page()
                job_links.extend(await extract_links(page, job_search_url, JOB_LINK_SELECTOR))

                for i, link in enumerate(job_links, start=1):
                    print(f'Scraping page {page_number} offer {i}')
                    complete_url = f'{RACINE_URL}{link}'
                    html = get_html(complete_url)
                    if html:
                        # Utiliser un dictionnaire pour chaque offre d'emploi
                        contract_data = await get_contract_elements(html, CONTRACT_INFO_SELECTOR, wttj_database)
                        company_data = await get_company_elements(html, COMPANY_INFO_SELECTOR, wttj_database)

                        # On ajoute les éléments individuels à la liste d'offres
                        wttj_database.extend([contract_data, company_data])

                        await asyncio.sleep(uniform(1, 3))
    except Exception as e:
        logging.error(f'Erreur inattendue : {e}')

    # Concaténez les listes de dictionnaires en une seule liste
    save_file(wttj_database, OUTPUT_DIR, 'wttj_database')


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit()

