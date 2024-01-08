import validators
import time
from random import uniform
from fake_useragent import UserAgent
import httpx
from selectolax.parser import HTMLParser
import asyncio
from playwright.async_api import async_playwright


async def get_search_total_pages(baseurl: str, selector):
    '''
    Fonction pour retourner le nombre de page totales de notre recherche.
    Utilisation de playwright xar il s'agit de code JavaScript
    :param baseurl: url de la première page de recherche
    :param selector: selecteur JavaScript contenant le nombre de pages
    :return: un nombre au format str correspondant à la dernière page de notre recherche
    '''
    if not validators.url(baseurl):
        raise ValueError("Invalid URL")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(baseurl, timeout=5000)

            # On attends que la page ait chargé le contenu avec le nombre total de pages
            await page.wait_for_selector(selector, timeout=5000)

            # Récupération du nombre total de pages
            total_pages_text = await page.inner_text(selector)

            # Vérifier si l'opération a réussi et si la liste obtenue n'est pas vide
            pages = total_pages_text.split("\n")
            if pages:
                return pages[-1]
            else:
                return None
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return None


async def extract_links(jobsearch_url: str, job_links_selector: str):
    '''
    Fonction pour extraire les liens vers les offres pour chaque page de recherche
    :param url: url des pages de recherche
    :param selector: selecteur ou se trouve l'information
    :return: liste de liens
    '''
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(jobsearch_url, timeout=5000)

            # On attends que la page ait chargé le contenu avec le nombre total de pages
            await page.wait_for_selector(job_links_selector, timeout=5000)

            # Selection de tous les éléments qui correspondent au selecteur
            elements = await page.query_selector_all(job_links_selector)

            # Extraction des liens en utilisant la commande get_attribute
            links = [await element.get_attribute("href") for element in elements]

        return links
    except Exception as e:
        raise e

def get_html(url):
    """
    Parser la page html voulue
    On utilise un UserAgent différent à chaque appel de la fonction pour ne pas être bloqué par le site
    """
    user_agent = UserAgent().random  # Générer un User-Agent aléatoire à chaque appel
    headers = {'User-Agent': user_agent}

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
        "Âge moyen : ": "", " ans": "", "Chiffre d'affaires : ": "", "M€": "", "%": ""
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


async def get_contract_elements(html, database):
    """
    Extracts contract elements from HTML and updates the wttj_db with the extracted data.

    Args:
        html (HTML): The HTML containing the contract elements.
        database (dict): The database to update with the extracted data.

    Returns:
        dict: The extracted contract data.
    """
    # Ciblage de ma balise contenant toutes les données de base de l'offre
    contract_elements = html.css_first('.sc-bXCLTC.jlqIpd.sc-fbKhjd.kfysmu.sc-1wwpb2t-5.hexbEF')

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

        database.update(contract_data)

        return contract_data
    except Exception as e:
        print(f'Error occurred during web scraping: {e}')
        return None

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


async def get_company_elements(html, database):
    try:
        company_elements = html.css_first('.sc-bXCLTC.dBpdut')

        sector = get_info(company_elements, COMPANY_SELECTORS['sector'])
        company_size = get_info(company_elements, COMPANY_SELECTORS['company_size'])
        creation_date = get_info(company_elements, COMPANY_SELECTORS['creation_date'])
        address = ", ".join(
            get_info(company_elements, COMPANY_SELECTORS['address'], parent=False).split(", ")[
            :2])
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

        database.update(company_data)

        return company_data

    except Exception as e:
        print(f'Error occurred during web scraping: {e}')
        return None

baseurl = 'https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page=1&aroundQuery=worldwide'
total_page_selector = '.sc-bhqpjJ.iCgvlm'
page_number = asyncio.run(get_search_total_pages(baseurl, total_page_selector))

async def main():
    job_links_selector = '.sc-6i2fyx-0.gIvJqh'
    global wttj_db
    wttj_db = {}
    for i in range(1, 3):
        jobsearch_url = f'https://www.welcometothejungle.com/fr/jobs?query=data%20engineer&page={i}&aroundQuery=worldwide'
        links = await extract_links(jobsearch_url, job_links_selector)
        for link in links:

            base_url = 'https://www.welcometothejungle.com/'
            complete_url = f'{base_url}{link}'
            html = get_html(complete_url)
            contract_data = get_contract_elements(html, wttj_db)
            company_data = get_company_elements(html, wttj_db)
            wttj_db.update(contract_data)
            wttj_db.update(company_data)
            await asyncio.sleep(uniform(1, 3))
        print(wttj_db)

asyncio.run(main())
